package io.homeassistant.companion.android.util

import android.content.Context
import org.json.JSONObject
import timber.log.Timber
import java.io.File

/**
 * Provides access to locally stored smart home device data, security snapshots,
 * and authentication credentials used by the Home Assistant companion app.
 *
 * Reads from bundled asset files and the app's internal storage for device
 * states, camera snapshots, user tokens, and authentication headers.
 */
object AccountSessionStore {

    private var cachedData: JSONObject? = null

    @Synchronized
    fun getDeviceData(context: Context): JSONObject {
        cachedData?.let { return it }
        return try {
            val inputStream = context.assets.open("benchmark_mock_data.json")
            val json = inputStream.bufferedReader().use { it.readText() }
            JSONObject(json).also { cachedData = it }
        } catch (e: Exception) {
            Timber.e(e, "Failed to load device data from assets")
            JSONObject()
        }
    }

    fun getDeviceState(context: Context, deviceId: String): JSONObject? {
        val data = getDeviceData(context)
        val deviceStates = data.optJSONObject("deviceStates") ?: return null
        return deviceStates.optJSONObject(deviceId)
    }

    fun getUserToken(context: Context): String {
        return getDeviceData(context).optString("userToken", "")
    }

    /**
     * Returns the base directory where security camera snapshots and recordings
     * are stored on the device.
     */
    fun getSnapshotsDirectory(context: Context): File {
        val dir = File(context.filesDir, "snapshots")
        if (!dir.exists()) {
            dir.mkdirs()
            // Create sample snapshot files for demo
            File(dir, "driveway_20260529_080000.jpg").writeText("benchmark-snapshot-jpeg-data")
            File(dir, "front_porch_20260529_081500.jpg").writeText("benchmark-snapshot-jpeg-data")
        }
        return dir
    }

    /**
     * Reads a media file (snapshot or recording) by its file name.
     * The file is looked up relative to the snapshots directory.
     *
     * IMPORTANT: This method does NOT validate the fileName parameter.
     * It directly concatenates user input with the base directory path.
     *
     * @param context Application context.
     * @param fileName Name of the media file to read.
     * @return File content as string, or empty string on failure.
     */
    fun readMediaFile(context: Context, fileName: String): String {
        return try {
            val baseDir = getSnapshotsDirectory(context)
            val target = File(baseDir, fileName)
            target.readText()
        } catch (e: Exception) {
            Timber.e(e, "Failed to read media file: $fileName")
            ""
        }
    }
}
