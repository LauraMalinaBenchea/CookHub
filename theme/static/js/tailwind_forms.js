/**
 * This javascript file should be included in the base template.
 *
 * This file contains JS which is used for all forms and all fields.
 */
$(document).ready(() => {
	// Disable autocomplete for datepicker fields.
	$(".dateinput").attr("autocomplete", "off");
});

$(document).on("focus", ".date-input input:not(.hasDatepicker)", function () {
	// Initializing every datepicker on page load causes visible lag.
	// Hence, we want to initialize datepicker when you click on it.
	$(this).datepicker(datepicker_conf);
});

$(document).on("submit", "form", function (event) {
	/**
	 * Allow only one submit per form and show a loading spinner for the used submit button.
	 */
	if (this.submitted) {
		event.preventDefault();
	} else {
		this.submitted = true;

		if (event.originalEvent) {
			// Could be `undefined` if the form is submitted programmatically.
			// Show the spinner only *once* here.
			let submitButton = $(event.originalEvent.submitter);
			submitButton.children().css("visibility", "hidden");
			submitButton.append('<i class="fa-solid fa-spin fa-spinner"></i>');
		}
	}
});
