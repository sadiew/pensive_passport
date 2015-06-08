var geocoder;
var map;
var cityLatLon;

function initialize(location) {
  var mapOptions = {
    zoom: 12,
  };

  map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

  geocoder = new google.maps.Geocoder();
  geocoder.geocode( { 'address': location }, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      map.setCenter(results[0].geometry.location);
      cityLatLon = results[0].geometry.location['A'] + ',' + results[0].geometry.location['F'];

      getPlaces();

      var marker = new google.maps.Marker({
        map: map,
        position: results[0].geometry.location
      });
    } else {
      alert('Geocode was not successful for the following reason: ' + status);
    }
  });


}

function getMapAndPlaces() {
  initialize(winningCity);
  $('#loading').hide();
}

function onPlaceClick(place, evt) {
  evt.preventDefault();
  getPlaceDetails(place);
}

function getPlaceDetails(place) {
  var request = {
    placeId: $(place).data("google-place-id")
  };

  var infowindow = new google.maps.InfoWindow();

  var service = new google.maps.places.PlacesService(map);
  service.getDetails(request, callback);

  function callback(placeObject, status) {
    if (status == google.maps.places.PlacesServiceStatus.OK) {
      var marker = new google.maps.Marker({
        map: map,
        position: placeObject.geometry.location
      });
      google.maps.event.addListener(marker, 'click', function() {
        infowindow.setContent(placeObject.name);
        infowindow.open(map, this);
      });

      var placeWebsite = placeObject.website;
      var placeUrl = placeObject.url;
      var placeRating = placeObject.rating || 'Unrated';

      var website = placeWebsite ? placeWebsite : placeUrl;

      var $description = $(place).next();
      $description.find('.rating').html(placeRating);
      $description.find('.website').attr('href', website);
    }
  }
}

function getPlaces() {
  $('#get-places-button').hide();
  addPlaceByType('restaurant');
  addPlaceByType('museum');
  addPlaceByType('park');

  $.get('/get-similar-trips?city_id=' + cityId,
      function (result) {
        $('#similar-trips').append('<h4 class="place-header align-center">Featured Recommendations</h4>');
        for (var item in result) {
          $('#similar-trips').append("<div class='col-md-3 align-center'>" +
                                       "<a href='/city/" + item + "' target='_blank'>" + result[item] + "</a>"+
                                     "</div>");
        }
      }
  );
}

function addPlaceByType(type) {
  $.post("/get-places",
         { city_id: cityId, city_lat_lon: cityLatLon, place_type: type },
         function (result) {
            var i = 0;
            for (var item in result) {
              var googlePlaceId = result[item];

              $('#' + type + '-info').append(
                "<div class='" + type + "'>" +
                  "<a data-target='#" + type + "-" + i + "' data-toggle='collapse'" +
                  "href='#' onclick='onPlaceClick(this, event)' data-google-place-id='" +
                  googlePlaceId + "'>" + item + "</a>" +
                  "<div id='" + type + "-" + i + "' class='collapse'>" +
                    "<div class='description'>" +
                      "<div>Average Rating: <span class='rating'></span> </div>" +
                      "<a href='#' target='_blank' class='website'>Website</a>" +
                    "</div>" +
                  "</div>" +
                "</div>");
              i++;
            }
         });
}

google.maps.event.addDomListener(window, 'load', getMapAndPlaces);