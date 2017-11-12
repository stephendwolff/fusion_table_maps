
function get_fusion_table_layer_query() {
    // return layers object, for re-use
    return {
        select: 'Location',
        from: google_fusion_table_id,
        where: "Location not equal to " + (5000000 - Math.random() * 99999999).toString()
    }
}

function initMap() {
    // used as callback on creation of google maps api
    // Center: Dorset, Dorchester, UK
    var map = new google.maps.Map(document.getElementById('map-canvas'), {
        center: new google.maps.LatLng(50.7092701,-2.4459305),
        zoom: 15,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    layer = new google.maps.FusionTablesLayer({
        query: get_fusion_table_layer_query(),
        map: map
    });

    layer.setMap(map);

    google.maps.event.addListener(map, 'click', function(event) {

        // reverse geocode latLng point,
        var geocoder = new google.maps.Geocoder();

        geocoder.geocode({'location': event.latLng}, function(results, status) {
            if (status === 'OK') {
                if (results[0]) {

                    // check type is 'address'
                    if (results[0].types[0] === "street_address") {

                        // prevent double clicks
                        if (!map_click_submit_in_progress) {

                            map_click_submit_in_progress = true;

                            // if valid, store in backend (which then stores in Google Fusion Table)
                            var posting = $.ajax({
                                type: 'POST',
                                url: save_map_location_url,
                                data: {
                                    lat: event.latLng.lat,
                                    lng: event.latLng.lng,
                                    address: results[0].formatted_address,
                                }
                            });

                            posting.done(function () {
                                map_click_submit_in_progress = false;
                                // trigger table and mapupdate
                                reload_fusion_table_and_map_markers();
                            });

                            posting.fail(function (jqXHR, textStatus) {
                                map_click_submit_in_progress = false;
                                alert (textStatus);
                            });
                        }

                    } else {
                        alert('Sorry, but no street address could be found for that location.');
                    }
                } else {
                    alert('No results found');
                }
            } else {
                alert('Geocoder failed due to: ' + status);
            }
        });
    });
}

function reload_fusion_table_and_map_markers() {
    // get the rows from the fusion table
    var table_get_url = 'https://www.googleapis.com/fusiontables/v2/query?sql=SELECT%20Location,%20Address%20from%20' +
        google_fusion_table_id + '&key=' + google_api_key + '&cacheBust=' + (Math.random() * 99999999).toString();

    $.get(table_get_url, function( data ){

        var table_html = "<table class='table'><thead><th>Location</th><th>Address</th></thead>";
        $.each(data["rows"], function( index, value) {
            table_html += "<tr><td>" + value[0] + "</td><td>" + value[1] + "</td></tr>";
        });
        table_html += "</table>";
        $("#map-table").html(table_html);
    });

    // check layer var has been created
    if (typeof layer !== 'undefined') {
        // force google map layer to refresh
        layer.setOptions({
            query: get_fusion_table_layer_query()
        });
    }
}

