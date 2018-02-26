/**
 * Created by Mauriel on 1/19/2018.
 */
$(document).on('click', ".mdl-chip__action.action_cancel", function () {
    $(this).closest(".message-container").remove();
});