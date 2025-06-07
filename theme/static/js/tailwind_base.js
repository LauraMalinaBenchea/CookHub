// * theme inside `tailwind/static_src/css/libs/tippy.css`
// * delegate(parent, {target: <selector}) will also initialize tooltips on dynamically added elements.
tippy.delegate("body", {
	target: "[data-tippy-content]",
	theme: "ls",
	allowHTML: true,
});
