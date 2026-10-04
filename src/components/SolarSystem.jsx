import Cobj from "./Cobj";
import MoonOrbitalPlane from "./MoonOrbitalPlane";
import SunMarsBinarySystem from "./SunMarsBinarySystem";

const SolarSystem = () => {
  return (
    <group>
      <Cobj name="SystemCenter">
        <Cobj name="Earth">
          <MoonOrbitalPlane live>
            <Cobj name="Moon deferent A">
              <Cobj name="Moon" />
            </Cobj>
            <Cobj name="Actual Moon deferent A">
              <Cobj name="Actual Moon" />
            </Cobj>
          </MoonOrbitalPlane>
          <SunMarsBinarySystem ObjectComponent={Cobj} trackLiveState />
        </Cobj>
      </Cobj>
    </group>
  );
};
export default SolarSystem;
