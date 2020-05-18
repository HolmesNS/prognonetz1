var coords = []; // CO-ORDINATES FOR STORING DATA OF GRID LINES
var pointList = []; // LIST OF POINTS TO BE USED FOR ADDING LINES
var mymap = ""; // WILL BE USED TO ALLOCATE LEAFLET MAP

/** LOAD GRID DATA FOR LINE AND SET FIRST LAT LONG AS CENTER OF THE MAP */
$.get("/static/data.json", function(data) {
  coords = data;

  // INITIATE LEAFLET MAP
  mymap = L.map("mapid").setView(
    [
      data.features[0].geometry.coordinates[1],
      data.features[0].geometry.coordinates[0]
    ],
    10
  );

  // SET TILE LAYER FROM STADAIMAPS
  L.tileLayer("https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png", {
    attribution:
      '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(mymap);

  // HERE WE ARE USING AJAX FUNCTION (https://api.jquery.com/jquery.ajax/) TO SEND
  // HTTP REQUEST TO SERVER FOR GETTING TEMP FOR GRID LINES
  $.ajax({
    type: "POST", // An alias for http request method.
    url: "/location_data", // URL WHERE REQUEST WILL BE SUBMITTED
    dataType: "json", // REQUEST DATA TYPE
    contentType: "application/json", // REQUEST HEADER TO LET SERVER KNOW THAT THIS REQUEST CONTENT IS JSON
    data: {}, // GETTING INPUTTED VALUE AND SENDING IN DATA

    // UPON SUCCESS RESPONSE DRAW LINES WITH APPROPRIATE COLORS
    success: function(res) {
      var tmp = res;
      var loc_temp = [];
      // STORE TEMPERATURES IN ARRAY TO BE MATCHED WITH EACH GRID POINT CO-ORDINATES
      for (var k in tmp) {
        loc_temp.push(tmp[k]);
      }

      // MATCH CO-ORDINATES OF GRID POINTS WITH TEMPERATURE OFFSETS IN ORDER TO SET LINE COLOR
      for (let i = 0; i < coords.features.length; i++) {
        if (coords.features[i + 1]) {
          // PREPATE POINT 1 TO DRAW LINE FROM - CURRENT GRID POINT
          var P1 = new L.LatLng(
            coords.features[i].geometry.coordinates[1],
            coords.features[i].geometry.coordinates[0]
          );

          // PREPARE POINT 2 TO DRAW LINE TO WHICH IS NEXT GRID POINT
          var P2 = new L.LatLng(
            coords.features[i + 1].geometry.coordinates[1],
            coords.features[i + 1].geometry.coordinates[0]
          );

          var color = ""; // DEFINE COLOR FOR GRID LINE
          var temp = parseInt(loc_temp[i]);

          // IF TEMPERATURE LESS THAN 60 THEN SET COLOR TO GREEN
          if (temp < 60) {
            color = "green";
          } else if (temp < 70) {
            // IF TEMPERATURE LESS THAN 70 THEN SET COLOR TO ORANGE
            color = "orange";
          } else if (temp > 70) {
            // IF TEMPERATURE LESS THAN 70 THEN SET COLOR TO RED
            color = "red";
          }

          // CREATE NEW LINE AND ADD IT TO A MAP
          // FIND MORE - https://leafletjs.com/reference-1.6.0.html#polyline
          var line = new L.polyline([P1, P2], {
            color: color,
            weight: 3, // BOLDNESS OF LINE
            opacity: 3, // OPACITY OF LINE
            smoothFactor: 1 // SMOOTHNESS
          });

          // ADD LINE TO LEAFLET MAP
          line.addTo(mymap);
        }
      }
    }
  });
});

// INITIALIZE ANGULAR MODULE
var app = angular.module("myApp", []);

// INITIAL CONFIGURATION OF ANGULAR APP
app.config(function($interpolateProvider) {
  // CONFIGURE TAGS TO DISPLAY DATA IN INDEX TEMPLATE
  $interpolateProvider.startSymbol("//").endSymbol("//");
});

// CONTROLLER FUNCTION FOR TRANS ANALYSIS FORM
app.controller("myCtrl", function($scope, $http, $interval) {
  // ANALYSIS FORM DATA
  $scope.data = {
    temperature: "",
    values: [
      {
        current: "",
        time: ""
      }
    ]
  };

  // KEEP REFRESHING AMP REALTIME IMAGE EVERY ONE MINUTE IN BACKGROUND
  $interval(function() {
    document.getElementById("imgrealtime").src =
      "/static/amp_realtime.png?v=" + Math.random();
  }, 60000);

  $scope.loading = false;

  // ADD MORE INPUTS FOR TRANSIENT ANALYSIS FORM
  $scope.addMore = function() {
    // PUSH INTO EXISTING ARRAY
    $scope.data.values.push({
      current: "",
      time: ""
    });
  };

  // REMOVE A INPUT ROW FROM TRANSIENT ANALYSIS FORM
  $scope.remove = function(idx) {
    // REMOVE FROM SPECIFIED INDEX
    $scope.data.values.splice(idx, 1);
  };

  // ADD TRANSIENT ANALYSIS FORM
  $scope.submit = function() {
    // DISABLE SUBMIT BUTTON UNTIL RESPONSE IS RECEIVED
    $scope.loading = true;

    // PREPARE PROPER REQUEST OBJECT, CONVERT DATA TO INTEGER
    $scope.data.temperature = parseFloat($scope.data.temperature);
    $scope.data.values.forEach(function(v) {
      v.current = parseFloat(v.current);
      v.time = parseFloat(v.time);
    });

    // SUBMIT REQUEST TO SERVER
    $http.post("/saveImage", $scope.data).then(
      function(res) {
        // SET WARNINGS FROM RESPONSE IF ANY
        console.log(res.data);
        if (res.data.warning1) {
          // SET FIRST WARNING
          $scope.warning1 = res.data.warning1;
        }
        if (res.data.warning2) {
          // SET SECOND WARNING
          $scope.warning2 = res.data.warning2;
        }

        // REFRESH NEWIMAGE AFTER GETTING RESPONSE BY ADDING RANDOM NUMBER IN THE END
        document.getElementById("img1").src =
          "/static/fig_choose.png?v=" + Math.random();

        // SCROLL TO TOP OF THE DIV
        $(".my-col").scrollTop(0);

        // ENABLE SUBMIT BUTTON BACK
        $scope.loading = false;
        // window.location.reload(true);
      },
      function(err) {
        // SHOW ERROR IN ALERT IF ANY
        alert(JSON.stringify(err));
        $scope.loading = false;
      }
    );
  };
});
