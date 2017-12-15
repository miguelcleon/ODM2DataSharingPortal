'use strict';

$(function() {
    const isEnabled = $('#id_is_enabled')[0];
    const syncType = $('#id_sync_type')[0];
    const updateFreq = $('#id_update_freq')[0];

    if (!isEnabled.checked) {
        syncType.setAttribute('disabled', true);
        updateFreq.setAttribute('disabled', true);
    } else if (syncType.value === 'M') {
        updateFreq.setAttribute('disabled', true);
    }

    isEnabled.onclick = function(e) {
        if (e.target.checked) {
            syncType.removeAttribute('disabled');
            if (syncType.value === 'S') {
                updateFreq.removeAttribute('disabled');
            } else {
                updateFreq.setAttribute('disabled', true);
            }
        } else {
            syncType.setAttribute('disabled', true);
            updateFreq.setAttribute('disabled', true);
        }
    };

    syncType.onchange = function(e) {
        if (e.target.value === 'S') {
            updateFreq.removeAttribute('disabled');
        } else {
            updateFreq.setAttribute('disabled', true);
        }
    };

    $('#site-registration-form').submit(function() {
        syncType.removeAttribute('disabled');
        updateFreq.removeAttribute('disabled');
    });

});