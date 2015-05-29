var geocoder;
    var map;
    var cityLatLon;

    function initialize(location) {
      geocoder = new google.maps.Geocoder();
      geocoder.geocode( { 'address': location}, function(results, status) {
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
      
      var mapOptions = {
        zoom: 12,

      }
      map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
    }

    function getMap() {
      initialize(winningCity);
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

      service = new google.maps.places.PlacesService(map);
      service.getDetails(request, callback)

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

        if (placeWebsite) {
          var website = placeWebsite}
        else {
          var website = placeUrl}

        var $description = $(place).next();
        console.log($description); 
        $description.find(".rating").html(placeRating);
        $description.find(".website").attr("href", website);
        
      }
        
      }
    }
    
    function getPlaces() {
        $('#get-places-button').hide();        
        addPlaceByType('restaurant');
        addPlaceByType('museum');
        addPlaceByType('park');

        $.get( "/get-similar-trips?city_id=" + cityId,
            function (result) {
                $('#similar-trips').append("<h4 class='secondary-color align-center'>Featured Recommendations</h4>"); 
                for (item in result) {
                    $('#similar-trips').append("<div class='col-md-3 align-center'><a href='/cities/" + item + "'>" + result[item] + "</a></div>");
                };
            }
        );
    };

    function addPlaceByType(type) {
      console.log(cityLatLon);
      $.post( "/get-" + type + 's',
            {city_id: cityId, city_lat_lon: cityLatLon},
            function (result) {
                var i=0;
                for (item in result) {
                    var googlePlaceId = result[item]
                
                    $('#' + type + '-info').append("<div class='" + type + "'>" +
                                                    "<a data-target='#" + type + "-" + i + "' data-toggle='collapse' href='#' onclick='onPlaceClick(this, event)' data-google-place-id='" + googlePlaceId + "'>" + item + "</a>" +
                                                    "<div id='" + type + "-" + i + "' class='collapse'>" +
                                                      "<div class='description'>" +
                                                        "<div>Average Rating: <span class='rating'></span> </div>" + 
                                                        "<a href='#' class='website'>Website</a>" +
                                                      "</div>" +
                                                    "</div>" +
                                                  "</div>");
                    i++;
                    };
                }
        );

    }

    google.maps.event.addDomListener(window, 'load', getMap);