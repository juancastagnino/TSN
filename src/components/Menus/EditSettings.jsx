import { useEffect, useMemo, useRef } from "react";
import { createPortal } from "react-dom";
import { useControls, useCreateStore, Leva, folder, button } from "leva";
import { useStore, useSettingsStore, usePosStore } from "../../store";
import {
  saveSettingsAsJson,
  loadSettingsFromFile,
} from "../../utils/saveAndLoadSettings";
import { getCelestialEditorGroups } from "../../utils/celestialSettingsSchema";

const updateSettingField = (setting, property, value, updateSetting) => {
  const cleanValue = value.replace(/\u200B/g, "");
  updateSetting({ id: setting.id, [property]: cleanValue });
};

const settingFields = [
  "size",
  "actualSize",
  "startPos",
  "speed",
  "rotationStart",
  "rotationSpeed",
  "tilt",
  "tiltb",
  "orbitRadius",
  "solarVariationRadius",
  "lunarPlaneBlend",
  "orbitCentera",
  "orbitCenterb",
  "orbitCenterc",
  "orbitTilta",
  "orbitTiltb",
  "amplitude",
  "phase",
  "axisX",
  "axisY",
  "axisZ",
];

const isZeroSettingValue = (value) => {
  if (typeof value !== "number" && typeof value !== "string") return false;
  const normalized = String(value).replace(/\u200B/g, "").trim();
  if (normalized === "") return false;
  const numericValue = Number(normalized);
  return Number.isFinite(numericValue) && numericValue === 0;
};

const getControls = (s, updateSetting) => {
  const fields = settingFields.filter((property) => s[property] !== undefined);

  return Object.fromEntries(
    fields.map((property) => [
      `${s.name}${property}`,
      {
        label: property,
        value: "\u200B" + s[property],
        editable: true,
        render: (get) => {
          const currentSetting = useSettingsStore
            .getState()
            .getSetting(s.id);
          return (
            Boolean(get("Show zero values")) ||
            !isZeroSettingValue(currentSetting?.[property] ?? s[property])
          );
        },
        onChange: (value) => {
          updateSettingField(s, property, value, updateSetting);
        },
      },
    ])
  );
};

const componentLabel = (component) =>
  component
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/^./, (letter) => letter.toUpperCase());

// The inner component containing the hooks only mounts when the menu is active
const EditSettingsPanel = () => {
  const showPlanets = useStore((s) => s.showPlanets);
  const setShowPlanets = useStore((s) => s.setShowPlanets);
  const shadeOrbits = useStore((s) => s.shadeOrbits);
  const setShadeOrbits = useStore((s) => s.setShadeOrbits);
  const setEditSettings = useStore((s) => s.setEditSettings); // NEW
  const positions = usePosStore((s) => s.positions);
  const { settings, updateSetting, resetSettings } = useSettingsStore();

  const initialDeferentStates = useRef({});

  // Highly targeted DOM injection for the X button
  useEffect(() => {
    const interval = setInterval(() => {
      // Find the deepest div containing ONLY the exact title text
      const textDiv = Array.from(document.querySelectorAll("div")).find(
        (el) =>
          el.textContent.trim() === "Edit Settings" && el.children.length === 0
      );

      if (textDiv) {
        // Leva's title bar is the immediate flex container wrapping this text
        const titleBar = textDiv.parentElement;

        if (titleBar && !titleBar.querySelector(".leva-close-x")) {
          // Allow the title bar to anchor our absolutely positioned button
          titleBar.style.position = "relative";

          const closeBtn = document.createElement("div");
          closeBtn.className = "leva-close-x";
          closeBtn.innerHTML = "✕";

          // Style it seamlessly into the top right corner
          Object.assign(closeBtn.style, {
            position: "absolute",
            right: "12px",
            top: "50%",
            transform: "translateY(-50%)",
            cursor: "pointer",
            color: "#8C92A4",
            fontSize: "14px",
            fontWeight: "bold",
            padding: "4px",
            zIndex: "9999",
          });

          // Native hover colors
          closeBtn.onmouseenter = () => (closeBtn.style.color = "#FFFFFF");
          closeBtn.onmouseleave = () => (closeBtn.style.color = "#8C92A4");

          // CRITICAL: Stop the click from passing through and triggering Leva's drag feature
          closeBtn.onmousedown = (e) => e.stopPropagation();

          // Close action
          closeBtn.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            setEditSettings(false);
          };

          titleBar.appendChild(closeBtn);
        }
      }
    }, 150);

    return () => clearInterval(interval);
  }, [setEditSettings]);

  useEffect(() => {
    // 1. Capture original visibility of all deferents on mount
    settings.forEach((s) => {
      if (
        s.name.includes("deferent") &&
        initialDeferentStates.current[s.name] === undefined
      ) {
        initialDeferentStates.current[s.name] = s.visible;
      }
    });

    // 2. Restore them back when menu closes - UNLESS the user explicitly changed them
    return () => {
      const currentStoreSettings = useSettingsStore.getState().settings;
      currentStoreSettings.forEach((s) => {
        if (s.name.includes("deferent")) {
          const originalVisibility = initialDeferentStates.current[s.name];
          if (
            originalVisibility !== undefined &&
            s.visible !== originalVisibility
          ) {
            useSettingsStore
              .getState()
              .updateSetting({ ...s, visible: originalVisibility });
          }
        }
      });
    };
  }, []);

  const settingsFolders = useMemo(() => {
    const showHideMenu = {};
    const settingsMenu = {};
    const editorGroups = getCelestialEditorGroups(settings);

    // Visibility belongs to a real celestial owner, never to one of its
    // internal geometry stages. This avoids name-based grouping and keeps Mars
    // and Eros stages below their bodies just like the Moon and Pluto stages.
    editorGroups.forEach((editorGroup) => {
      editorGroup.bodies.forEach((body) => {
        const main = body.settings.find((setting) => setting.id === body.id);
        if (typeof main?.visible !== "boolean") return;
        showHideMenu[`${body.name}visible`] = {
          label: body.name,
          value: main.visible,
          editable: true,
          onChange: (value, path, context) => {
            const isInitialSync = context ? context.initial : main.visible === value;
            updateSetting({ id: main.id, visible: value });
            if (!isInitialSync) {
              initialDeferentStates.current[main.name] = value;
            }
          },
        };
      });
    });

    // The edit menu follows the declared astronomical system rather than
    // inferring parentage from display-name substrings.
    editorGroups.forEach((editorGroup) => {
      const groupControls = {};
      editorGroup.bodies.forEach((body) => {
        const bodyControls = {};
        if (body.frames.length > 0) {
          body.frames.forEach((frame) => {
            const frameControls = {};
            frame.settings.forEach((setting) => {
              frameControls[setting.name] = folder(
                getControls(setting, updateSetting),
                { collapsed: true }
              );
            });
            bodyControls[frame.name] = folder(frameControls, {
              collapsed: true,
            });
          });
        } else {
          body.settings.forEach((setting) => {
            bodyControls[componentLabel(setting.component)] = folder(
              getControls(setting, updateSetting),
              { collapsed: true }
            );
          });
        }
        groupControls[body.name] = folder(bodyControls, { collapsed: true });
      });
      settingsMenu[editorGroup.name] = folder(groupControls, {
        collapsed: true,
      });
    });

    return {
      "Load settings": button(() => loadSettingsFromFile()),
      "Save settings": button(() => saveSettingsAsJson()),
      "Reset settings": button(() => resetSettings()),
      "Show zero values": {
        value: false,
        label: "Show zero values",
      },
      "Show / Hide Planets": {
        value: showPlanets,
        onChange: (v) => setShowPlanets(v),
      },
      "Filled Orbits": {
        value: shadeOrbits,
        onChange: (v) => setShadeOrbits(v),
      },
      "Show / Hide settings": folder(showHideMenu, { collapsed: false }),
      Settings: folder(settingsMenu, { collapsed: false }),
    };
  }, [
    settings,
    updateSetting,
    showPlanets,
    setShowPlanets,
    shadeOrbits,
    setShadeOrbits,
  ]);

  const levaSettingsStore = useCreateStore();

  const [, set] = useControls(() => settingsFolders, {
    store: levaSettingsStore,
  });

  useEffect(() => {
    const updatedValues = {
      "Show / Hide Planets": showPlanets,
      "Filled Orbits": shadeOrbits,
    };
    const visibilitySettingIds = new Set(
      getCelestialEditorGroups(settings).flatMap((editorGroup) =>
        editorGroup.bodies
          .map((body) => body.settings.find((setting) => setting.id === body.id))
          .filter((setting) => typeof setting?.visible === "boolean")
          .map((setting) => setting.id)
      )
    );
    settings.forEach((s) => {
      if (visibilitySettingIds.has(s.id)) {
        updatedValues[`${s.name}visible`] = s.visible;
      }
      settingFields.forEach((property) => {
        if (s[property] !== undefined) {
          updatedValues[`${s.name}${property}`] = "\u200B" + s[property];
        }
      });
    });
    set(updatedValues);
  }, [settings, set, showPlanets, shadeOrbits]);

  return createPortal(
    <div
      className="settings-div"
      style={{
        position: "fixed",
        top: "80px",
        right: "10px",
        zIndex: 2147483647,
      }}
    >
      <Leva
        store={levaSettingsStore}
        titleBar={{ drag: true, title: "Edit Settings", filter: false }}
        fill={false}
        hideCopyButton
        theme={{
          fontSizes: {
            root: "12px",
          },
          fonts: {
            mono: "",
          },
          colors: {
            highlight1: "#FFFFFF",
            highlight2: "#FFFFFF",
          },
        }}
      />
    </div>,
    document.body
  );
};

const EditSettings = () => {
  const editSettings = useStore((s) => s.editSettings);

  if (!editSettings) return null;

  return <EditSettingsPanel />;
};

export default EditSettings;
