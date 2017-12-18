'use strict';

$(function() {
    resizeHSConnectionLinkButton();
});

function resizeHSConnectionLinkButton() {
    const addHsConnLink = $('a#hs-conn-link');
    addHsConnLink.width(addHsConnLink.innerWidth());
}