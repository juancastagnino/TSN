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
          <SunMarsBinarySystem ObjectComponent={Cobj} />
          <Cobj name="Eros deferent A">
            <Cobj name="Eros deferent B">
              <Cobj name="Eros" />
            </Cobj>
          </Cobj>
        </Cobj>
      </Cobj>
    </group>
  );
};
export default SolarSystem;
