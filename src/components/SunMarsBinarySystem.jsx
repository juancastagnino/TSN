import React from "react";
import ErosSunRelativeOrbit from "./ErosSunRelativeOrbit";
import MercurySunRelativeOrbit from "./MercurySunRelativeOrbit";
import SunMarsBinaryTracker from "./SunMarsBinaryTracker";
import SunMarsRelativeOrbit from "./SunMarsRelativeOrbit";
import VenusSunRelativeOrbit from "./VenusSunRelativeOrbit";

/**
 * Shared semantic frame for the TYCHOS Sun-Mars primary-companion system.
 *
 * The named branches and relative-component transforms are deliberately
 * coordinate preserving: they re-express the accepted settings without fitting
 * new orbital parameters. Keeping both the visual and plot models on this
 * component prevents their hierarchies from drifting apart.
 */
const SunMarsBinarySystem = ({
  ObjectComponent,
  trackLiveState = false,
  plotMode = false,
}) => {
  const ObjectNode = ObjectComponent;

  return (
    <group name="Sun-Mars Binary Frame">
      <group name="Sun Primary Branch">
        <ObjectNode name="Sun deferent">
          <ObjectNode name="Sun">
            <ObjectNode name="Halleys deferent">
              <ObjectNode name="Halleys" />
            </ObjectNode>
            <ObjectNode name="Jupiter deferent">
              <ObjectNode name="Jupiter" />
            </ObjectNode>
            <ObjectNode name="Saturn deferent">
              <ObjectNode name="Saturn" />
            </ObjectNode>
            <ObjectNode name="Uranus deferent">
              <ObjectNode name="Uranus" />
            </ObjectNode>
            <ObjectNode name="Neptune deferent">
              <ObjectNode name="Neptune" />
            </ObjectNode>
            <ObjectNode name="Pluto deferent">
              <ObjectNode name="Pluto" />
            </ObjectNode>
            <SunMarsRelativeOrbit
              name="Sun-Relative Mars Components"
              plotMode={plotMode}
            >
              <group name="Mars Junior Companion Branch">
                <ObjectNode name="Mars">
                  <ObjectNode name="Phobos" />
                  <ObjectNode name="Deimos" />
                </ObjectNode>
              </group>
            </SunMarsRelativeOrbit>
            <VenusSunRelativeOrbit
              name="Sun-Relative Venus Frame"
              plotMode={plotMode}
            >
              <group name="Venus Senior Solar Companion Branch">
                <ObjectNode name="Venus" />
              </group>
            </VenusSunRelativeOrbit>
            <MercurySunRelativeOrbit
              name="Sun-Relative Mercury Frame"
              plotMode={plotMode}
            >
              <group name="Mercury Junior Solar Companion Branch">
                <ObjectNode name="Mercury" />
              </group>
            </MercurySunRelativeOrbit>
            <ErosSunRelativeOrbit
              name="Sun-Relative Eros Frame"
              plotMode={plotMode}
            >
              <group name="Eros Solar Asteroid Branch">
                <ObjectNode name="Eros" />
              </group>
            </ErosSunRelativeOrbit>
          </ObjectNode>
        </ObjectNode>
      </group>

      {trackLiveState && <SunMarsBinaryTracker />}
    </group>
  );
};

export default SunMarsBinarySystem;
