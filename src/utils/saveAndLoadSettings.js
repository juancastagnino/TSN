import { useSettingsStore } from "../store";
import { serializeCelestialSettings } from "./celestialSettingsSchema";

export const saveSettingsAsJson = (settings) => {
  // Native schema v2 retains stable IDs and rotationStart. Older flat arrays
  // remain accepted by the loader for compatibility with existing authors.
  const jsonString = JSON.stringify(serializeCelestialSettings(settings), null, 2);

  // Create a Blob with the JSON content
  const blob = new Blob([jsonString], { type: "application/json" });

  // Create a temporary URL for the Blob
  const url = URL.createObjectURL(blob);

  // Generate timestamp for filename (YYYYMMDD_HHMM)
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
  const timestamp = `${year}${month}${day}_${hours}${minutes}`;

  // Create a temporary anchor element to trigger the download
  const link = document.createElement("a");
  link.href = url;
  link.download = `TS_settings_${timestamp}.txt`; // Set the filename with timestamp
  document.body.appendChild(link);
  link.click();

  // Clean up
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export const loadSettingsFromFile = async () => {
  try {
    // Create file input element
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".txt,.json";

    // Wrap file selection in a promise
    const file = await new Promise((resolve) => {
      input.onchange = (e) => resolve(e.target.files[0]);
      input.click();
    });

    if (!file) return; // User cancelled

    // Read file contents
    const fileContents = await file.text();
    const parsedSettings = JSON.parse(fileContents);

    // One atomic update supports both schema-v2 documents and legacy arrays.
    useSettingsStore.getState().loadSettings(parsedSettings);

    return true; // Success
  } catch (error) {
    console.error("Error loading settings:", error);
    alert(`Error loading settings: ${error.message}`);
    return false;
  }
};

