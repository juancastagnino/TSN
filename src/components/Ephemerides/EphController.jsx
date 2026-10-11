import { useEffect, useState, useRef } from "react";
import { useThree, useFrame } from "@react-three/fiber";
import { usePlotStore } from "../../store";
import { useEphemeridesStore } from "./ephemeridesStore";
import {
  posToDate,
  posToTime,
  dateTimeToPos,
  addYears,
  addMonths,
  sYear,
  sMonth,
} from "../../utils/time-date-functions";
import {
  EPHEMERIS_REFERENCE_FRAMES,
  getJ2000EarthFrameQuaternion,
  getPlotSunMarsBinaryDiagnostics,
  movePlotModel,
  getPlotModelRaDecDistance,
} from "../../utils/plotModelFunctions";
import { createSunMarsBinaryDiagnostics } from "../../utils/sunMarsBinaryState";
import { sunMarsBinaryDiagnosticsToRow } from "../../utils/sunMarsBinaryCsv";

const EphController = () => {
  const { invalidate } = useThree();
  const plotObjects = usePlotStore((s) => s.plotObjects);

  const {
    trigger,
    params,
    resetTrigger,
    setGeneratedData,
    setGenerationError,
    setIsGenerating,
    setProgress,
  } = useEphemeridesStore();

  const [generating, setGenerating] = useState(false);
  const binaryDiagnosticsRef = useRef(createSunMarsBinaryDiagnostics());

  const jobRef = useRef({
    startPos: 0,
    currentStep: 0,
    totalSteps: 0,
    increment: 0,
    checkedPlanets: [],
    referenceFrame: EPHEMERIS_REFERENCE_FRAMES.TYCHOS_NATIVE,
    j2000Quaternion: null,
    data: {},
    binaryDiagnostics: false,
    binaryRows: [],
    lastProgress: 0,
  });

  // 1. Initialize Job
  useEffect(() => {
    if (trigger && params) {
      setIsGenerating(true);
      setProgress(0);

      const startPos = dateTimeToPos(params.startDate, "00:00:00");
      const endPos = dateTimeToPos(params.endDate, "00:00:00");
      let increment = params.stepSize * params.stepFactor;

      // Reverse direction if Start > End
      if (startPos > endPos) {
        increment = -increment;
      }

      const totalSteps = Math.round((endPos - startPos) / increment);
      const referenceFrame =
        params.referenceFrame || EPHEMERIS_REFERENCE_FRAMES.TYCHOS_NATIVE;
      const j2000Quaternion =
        referenceFrame === EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF
          ? getJ2000EarthFrameQuaternion(plotObjects)
          : null;
      if (
        referenceFrame === EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF &&
        !j2000Quaternion
      ) {
        setGenerationError(
          "Unable to construct the J2000 Earth reference frame.\nPlease wait for the plot model to finish loading and try again."
        );
        resetTrigger();
        return;
      }

      // Initialize Data Structure
      const initialData = {};
      params.checkedPlanets.forEach((planet) => {
        initialData[planet] = [];
      });

      // Setup Job
      jobRef.current = {
        startDate: params.startDate,
        stepSize: params.stepSize,
        stepFactor: params.stepFactor,
        startPos: startPos,
        currentStep: 0,
        totalSteps: totalSteps,
        increment: increment,
        checkedPlanets: params.checkedPlanets,
        referenceFrame,
        j2000Quaternion,
        data: initialData,
        binaryDiagnostics: params.binaryDiagnostics === true,
        binaryRows: [],
        lastProgress: 0,
      };

      setGenerating(true);
      resetTrigger();
    }
  }, [
    trigger,
    params,
    resetTrigger,
    setGenerationError,
    setIsGenerating,
    setProgress,
    plotObjects,
  ]);

  // 2. Process Job in Chunks
  useFrame(() => {
    // Check for Cancellation
    if (generating && !useEphemeridesStore.getState().isGenerating) {
      setGenerating(false);
      return;
    }

    if (!generating) return;

    // Keep the loop alive while generating
    invalidate();

    const job = jobRef.current;
    const BATCH_SIZE = 50;
    let batchCount = 0;

    while (job.currentStep <= job.totalSteps && batchCount < BATCH_SIZE) {
      let currentPos, currentDate, currentTime;

      // Pin to the original exact start time (e.g., "00:00:00")
      const startTime = posToTime(job.startPos);

      // Calendar-aware stepping to prevent time-of-day drift
      if (job.stepFactor === sYear) {
        const dir = job.increment < 0 ? -1 : 1;
        currentDate = addYears(
          job.startDate,
          job.stepSize * job.currentStep * dir
        );
        currentTime = startTime;
        currentPos = dateTimeToPos(currentDate, currentTime);
      } else if (job.stepFactor === sMonth) {
        const dir = job.increment < 0 ? -1 : 1;
        currentDate = addMonths(
          job.startDate,
          job.stepSize * job.currentStep * dir
        );
        currentTime = startTime;
        currentPos = dateTimeToPos(currentDate, currentTime);
      } else {
        // Fallback for days, hours, minutes
        currentPos = job.startPos + job.currentStep * job.increment;
        currentDate = posToDate(currentPos);
        currentTime = posToTime(currentPos);
      }

      movePlotModel(plotObjects, currentPos);

      if (job.binaryDiagnostics) {
        const diagnostics = getPlotSunMarsBinaryDiagnostics(
          plotObjects,
          binaryDiagnosticsRef.current
        );
        const row = sunMarsBinaryDiagnosticsToRow(
          currentDate,
          currentTime,
          diagnostics
        );
        if (row) job.binaryRows.push(row);
      }

      job.checkedPlanets.forEach((name) => {
        const data = getPlotModelRaDecDistance(name, plotObjects, {
          referenceFrame: job.referenceFrame,
          j2000Quaternion: job.j2000Quaternion,
        });
        if (data) {
          job.data[name].push({
            date: currentDate,
            time: currentTime,
            ra: data.ra,
            dec: data.dec,
            dist: data.dist,
            elong: data.elongation,
          });
        }
      });

      job.currentStep++;
      batchCount++;
    }

    const progress = Math.min(
      100,
      Math.floor((job.currentStep / (job.totalSteps + 1)) * 100)
    );

    if (progress > job.lastProgress) {
      setProgress(progress);
      job.lastProgress = progress;
    }

    // Completion Check
    if (job.currentStep > job.totalSteps) {
      if (job.binaryDiagnostics && job.binaryRows.length === 0) {
        setGenerationError(
          "Sun-Mars binary diagnostics could not find the SystemCenter, Earth, Sun and Mars pivots."
        );
      } else {
        setGeneratedData(job.data, job.binaryRows);
      }
      setGenerating(false);
      setProgress(100);
    }
  });

  return null;
};
export default EphController;
