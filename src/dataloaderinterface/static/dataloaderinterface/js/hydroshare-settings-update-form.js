/**
 * @depracated This file will be removed once hydroshare settings are set using a modal instead of through a django form
 */
'use strict';

$(function() {
    const accountsFieldId = '#id_hs_account';
    const isEnabledId = '#id_is_enabled';
    const syncTypeId = '#id_sync_type';
    const updateFreqId = '#id_update_freq';
    const switchLabelId = '#is_enabled_switch_label';
    const hsSettingsFormGroupId = '#hs_settings_form_group';
    const registrationFormId = '#site-registration-form';

    function addEventListeners() {
        setInitialStates();

        $(accountsFieldId).change(function(ev) {
            try {
                if (ev.target.value.length) {
                    $(hsSettingsFormGroupId).show();
                } else {
                    $(hsSettingsFormGroupId).hide();
                }
                setReadOnlyModes();
            } catch(e) {
                $(hsSettingsFormGroupId).hide();
            }
        });

        $(isEnabledId).click(function(ev) {
            const switchLabel = $(switchLabelId)[0];
            const syncTypeEl = $(syncTypeId)[0];
            const updateFreqEl = $(updateFreqId)[0];

            switchLabel.innerText = ev.target.checked ? 'Syncing On' : 'Syncing Off';

            if (ev.target.checked) {
                syncTypeEl.removeAttribute('disabled');
                if (syncTypeEl.value === 'S') {
                    updateFreqEl.removeAttribute('disabled');
                } else {
                    updateFreqEl.setAttribute('disabled', true);
                }
            } else {
                syncTypeEl.setAttribute('disabled', true);
                updateFreqEl.setAttribute('disabled', true);
            }
        });

        $(syncTypeId).change(function(e) {
            const updateFreqEl = $(updateFreqId)[0];
            if (e.target.value === 'S') {
                updateFreqEl.removeAttribute('disabled');
            } else {
                updateFreqEl.setAttribute('disabled', true);
            }
        });

        $(registrationFormId).submit(function() {
            $(syncTypeId)[0].removeAttribute('disabled');
            $(updateFreqId)[0].removeAttribute('disabled');
        });
    }

    function setInitialStates() {
        const accountFieldEle = $(accountsFieldId)[0];
        if (accountFieldEle.value.length) {
            setReadOnlyModes();
        } else {
            $(hsSettingsFormGroupId).hide();
        }
    }

    function setReadOnlyModes() {
        const accountFieldEl = $(accountsFieldId)[0];
        const isEnabledEl = $(isEnabledId)[0];
        const syncTypeEl = $(syncTypeId)[0];
        const updateFreqEl = $(updateFreqId)[0];

        if (accountFieldEl.value && accountFieldEl.value.length) {
            if (!isEnabledEl.checked) {
                syncTypeEl.setAttribute('disabled', true);
                updateFreqEl.setAttribute('disabled', true);
            } else if (syncTypeEl.value === 'M') {
                updateFreqEl.setAttribute('disabled', true);
            } else {
                syncTypeEl.removeAttribute('disabled');
                updateFreqEl.removeAttribute('disabled');
            }
        } else {
            syncTypeEl.setAttribute('disabled', false);
            updateFreqEl.setAttribute('disabled', false);
        }
    }

    if ($(isEnabledId)[0]) {
        addEventListeners();
    }

});