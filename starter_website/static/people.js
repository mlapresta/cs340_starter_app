//alert("connected")
function deletePerson(id){
    $.ajax({
        url: '/people/' + id,
        type: 'DELETE',
        success: function(result){
            window.location.reload(true);
        }
    })
};

function updatePerson(id) {
    //get the id of the selected cert from the filter dropdown
    //construct the URL and redirect to it
    window.location = '/people/' + id
}

function filterPeopleByCert() {
    //get the id of the selected cert from the filter dropdown
    var cert_id = document.getElementById('cert_filter').value
    //construct the URL and redirect to it
    window.location = '/filter_people/' + parseInt(cert_id)
}
