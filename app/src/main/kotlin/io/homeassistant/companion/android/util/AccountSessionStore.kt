package io.homeassistant.companion.android.util

import android.content.Context
import org.json.JSONObject
import timber.log.Timber

/**
 * Provides access to locally stored smart home device configuration and state data.
 *
 * Reads from a bundled asset file containing device states, user tokens, and
 * authentication headers used by the Home Assistant companion app for device
 * control and status reporting.
 */
object AccountSessionStore {

    private var cachedData: JSONObject? = null

    /**
     * Returns the full device state and credential data as a [JSONObject].
     * The data is lazily loaded from assets and cached for the process lifetime.
     *
     * @param context Application or Activity context for accessing assets.
     * @return Parsed JSON data, or an empty JSONObject on failure.
     */
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

    /**
     * Returns the state for a specific device by its entity ID.
     *
     * @param context Application or Activity context for accessing assets.
     * @param deviceId The Home Assistant entity ID (e.g. "lock.front_door").
     * @return Device state JSONObject, or null if not found.
     */
    fun getDeviceState(context: Context, deviceId: String): JSONObject? {
        val data = getDeviceData(context)
        val deviceStates = data.optJSONObject("deviceStates") ?: return null
        return deviceStates.optJSONObject(deviceId)
    }

    /**
     * Returns the current user authentication token stored in the local device data.
     *
     * @param context Application or Activity context for accessing assets.
     * @return The user token string, or empty string if unavailable.
     */
    fun getUserToken(context: Context): String {
        val data = getDeviceData(context)
        return data.optString("userToken", "")
    }

    /**
     * Returns the full Authorization header value stored in the local device data.
     *
     * @param context Application or Activity context for accessing assets.
     * @return The Authorization header string, or empty string if unavailable.
     */
    fun getAuthorizationHeader(context: Context): String {
        val data = getDeviceData(context)
        return data.optString("authHeader", "")
    }
}
