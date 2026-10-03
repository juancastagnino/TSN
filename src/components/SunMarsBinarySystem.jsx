import React from "react";

/**
 * Shared semantic frame for the TYCHOS Sun-Mars binary.
 *
 * This first-stage refactor is deliberately coordinate preserving. The identity
 * groups name the physical roles without adding transforms, while the existing
 * Cobj/Pobj chains continue to produce the validated world positions. Keeping
 * both the visual and plot models on this component prevents their hierarchies
 * from drifting apart during later binary-geometry experiments.
 */
const SunMarsBinarySystem = ({ ObjectComponent }) => {
  const ObjectNode = ObjectComponent;

  return (
    <group name="Sun-Mars Binary Frame">
      <group name="Sun Companion Branch">
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
          </ObjectNode>
        </ObjectNode>
      </group>

      {/*
       * These carriers currently reconstruct the Sun-following motion without
       * inheriting the Sun object. They stay unchanged until a solar-host frame
       * can replace them with demonstrated ephemeris equivalence.
       */}
      <group name="Solar Moon Carrier Branches">
        <ObjectNode name="Venus deferent A">
          <ObjectNode name="Venus deferent B">
            <ObjectNode name="Venus Plane">
              <ObjectNode name="Venus" />
            </ObjectNode>
          </ObjectNode>
        </ObjectNode>
        <ObjectNode name="Mercury deferent A">
          <ObjectNode name="Mercury deferent B">
            <ObjectNode name="Mercury Plane">
              <ObjectNode name="Mercury" />
            </ObjectNode>
          </ObjectNode>
        </ObjectNode>
      </group>

      <group name="Mars Companion Branch">
        <ObjectNode name="Mars deferent E">
          <ObjectNode name="Mars deferent S">
            <ObjectNode name="Mars">
              <ObjectNode name="Phobos" />
              <ObjectNode name="Deimos" />
            </ObjectNode>
          </ObjectNode>
        </ObjectNode>
      </group>
    </group>
  );
};

export default SunMarsBinarySystem;
