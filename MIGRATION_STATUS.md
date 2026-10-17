# TSOG migration experiment

This branch is an isolated experiment based on Patrik's `TSOG_Work` engine.
It does not modify the accepted `full-send-binary-tychos` baseline.

## First structural integration

`scripts/convert-fullsend-model.mjs` converts the active hierarchy-refinement
schema-v3 model into TSOG's schema-v4 `objects[]` / `parentId` representation. It writes
both `src/settings/celestial-model.json` and its matching display catalogue.

The generated tree contains 41 stages, including:

- Earth, renamed Moon node/plane stages, explicit node counterrotation, apsidal
  geometry, apsidal equant and solar-coupled lunar geometry;
- the Earth-hosted Sun--Mars binary frame and Sun primary frame;
- Sun-hosted Mercury, Venus, Mars, outer planets, Pluto, Halley and Eros;
- Mars-hosted Phobos and Deimos; and
- Pluto's ordered deferent and eccentric stages; and
- Eros's Sun-relative annual frame, annual centre oscillation and local deferent.

This proves that TSOG's flat list can encode the current *structural* tree. A
flat JSON list is still a hierarchy because `parentId` defines its tree.

## Not yet an equivalence claim

This pass deliberately preserves the operation metadata in JSON, but TSOG's
ordinary generic circle/centre/tilt evaluator does not yet interpret the named
operations. It has not yet ported the specialised semantics of the model:

- Sun-relative frame anchoring used by Mars, Mercury, Venus and Eros;
- Eros axial annual-centre oscillation;
- lunar off-centre phase/equant geometry and solar-coupled centre geometry; and
- any future generic operation required by numerical comparison.

Therefore the buildable structural tree is an integration checkpoint, not an
accepted astronomical replacement. The next step is to introduce documented,
generic motion-operation types into TSOG and validate each one against identical
dates in the full-send baseline.
