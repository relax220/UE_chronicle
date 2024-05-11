function btnNamesCollapse(el) {
  s = el.innerHTML
  console.log(s)
  if (el.innerHTML === "Люди V") el.innerHTML = "Люди Ʌ";
  else el.innerHTML = "Люди V";
}
function btnPlacesCollapse(el) {
  s = el.innerHTML
  console.log(s)
  if (el.innerHTML === "Места V") el.innerHTML = "Места Ʌ";
  else el.innerHTML = "Места V";
}