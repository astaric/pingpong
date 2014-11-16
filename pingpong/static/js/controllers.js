'use strict';

/* Controllers */

var pingpongControllers = angular.module('pingpongControllers', ['ngDraggable', 'ngCookies']);

//+ Jonas Raoni Soares Silva
//@ http://jsfromhell.com/array/shuffle [v1.0]
function shuffled(o) { //v1.0
    o = o.slice(0);
    for (var j, x, i = o.length; i; j = Math.floor(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
    return o;
}

pingpongControllers.controller('CreateGroupsCtrl', ['$scope', '$http', '$cookieStore',
    function ($scope, $http, $cookieStore) {
        var playerMap = {}, idx, categoryId,
            redirectUrl, saveUrl,
            leaderCookie, othersCookie;

        $scope.message = 'Hello World!';
        $scope.numberOfGroups = 0;
        $scope.groups = [];
        $scope.leaders = [];
        $scope.others = [];

        $scope.updateGroups = function () {
            var groups = [], clubs = [];
            for (var i = 0; i < $scope.numberOfGroups; i++) {
                groups.push([]);
                clubs.push({})
            }

            var g = 0;

            function addToGroups(p) {
                groups[g].push(p);
                g = (g + 1) % $scope.numberOfGroups;
            }

            $scope.leaders.forEach(addToGroups);
            $scope.others.forEach(addToGroups);

            $scope.groups = groups;
        };

        function saveToCookies() {
            var leaderIds = [], otherIds = [];
            $scope.leaders.forEach(function (p) {
                leaderIds.push(p.id);
            });
            $scope.others.forEach(function (p) {
                otherIds.push(p.id);
            });

            $cookieStore.put(leaderCookie, leaderIds);
            $cookieStore.put(othersCookie, otherIds);
        }

        $scope.saveToServer = function() {
            if ($scope.others.length != $scope.players.length)
                $scope.drawOthers();

            $http.post(saveUrl, $scope.groups).
              success(function(data, status, headers, config) {
                location.href = redirectUrl;
              }).
              error(function(data, status, headers, config) {
                // called asynchronously if an error occurs
                // or server returns response with an error status.
              });
        };

        $scope.addLeader = function (p) {
            if (p.leader == false) {
                idx = $scope.players.indexOf(p);
                if (idx !== -1)
                    $scope.players.splice(idx, 1);
                p.leader = true;
                $scope.leaders.push(p);

                $scope.others = [];
                $scope.updateGroups();
                saveToCookies();
            }
        };

        $scope.removeLeader = function (p) {
            if (p.leader == true) {
                idx = $scope.leaders.indexOf(p);
                if (idx !== -1)
                    $scope.leaders.splice(idx, 1);
                p.leader = false;
                $scope.players.push(p);

                $scope.others = [];
                $scope.updateGroups();
                saveToCookies();
            }
        };

        $scope.drawOthers = function () {
            var shuffledPlayers = shuffled($scope.players);
            var others = [];

            var clubs = [];
            var g = 0;
            $scope.groups.forEach(function (g) {
                clubs.push({})
            });
            $scope.leaders.forEach(function (p) {
                if (p.club)
                    clubs[g][p.club] = true;
                g = (g + 1) % $scope.numberOfGroups;
            });
            function drawPlayer() {
                for (var i = 0; i < shuffledPlayers.length; i++) {
                    var p = shuffledPlayers[i];
                    if (!clubs[g][p.club]) {
                        if (p.club)
                            clubs[g][p.club] = true;
                        return shuffledPlayers.splice(i, 1)[0];
                    }
                }
                return shuffledPlayers.splice(0, 1)[0];
            }

            while (shuffledPlayers.length > 0) {
                others.push(drawPlayer());
                g = (g + 1) % $scope.numberOfGroups;
            }
            $scope.others = others;
            $scope.updateGroups();

            saveToCookies();
        };

        $scope.reset = function() {
            $cookieStore.remove(leaderCookie);
            $cookieStore.remove(othersCookie);
            reloadPlayers();
        };

        function reloadPlayers() {
            $http.get("/category/" + categoryId + '/players.json')
                .success(function (response) {
                    $scope.numberOfGroups = Math.ceil(response.length / 4);

                    var leaders = {};
                    var leaderIds = $cookieStore.get(leaderCookie) || [];
                    leaderIds.forEach(function (lId) {
                        leaders[lId] = true;
                    });
                    var otherIds = $cookieStore.get(othersCookie) || [];


                    $scope.players = [];
                    $scope.leaders = [];
                    $scope.others = [];
                    response.forEach(function (p) {
                        playerMap[p.id] = p;
                        if (leaders[p.id])
                            p.leader = true;
                        else
                            $scope.players.push(p);
                    });
                    leaderIds.forEach(function (lId) {
                        if (playerMap[lId]) {
                            $scope.leaders.push(playerMap[lId]);
                        }
                    });
                    otherIds.forEach(function (lId) {
                        if (playerMap[lId]) {
                            $scope.others.push(playerMap[lId]);
                        }
                    });

                    $scope.updateGroups()
                });
        }

        $scope.init = function (id) {
            categoryId = id;
            saveUrl = '/category/' + categoryId + '/groups/create_ng/';
            redirectUrl = '/category/' + categoryId + '/';
            leaderCookie = 'category' + id + 'leaders';
            othersCookie = 'category' + id + 'others';

            reloadPlayers();
        };
    }
])
;
