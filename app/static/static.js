
function displayAddressFields() {
	var checkBox = document.getElementById('address');
	var fields = document.getElementById('address_optional');

	if (checkBox.checked == false) {
		fields.style.display = 'block';
	} else {
		fields.style.display = 'none';
	}
}