'use strict';

/* App Module */

var pingpongApp = angular.module('pingpongApp', ['pingpongControllers']);
pingpongApp.config(function($interpolateProvider, $httpProvider) {
  $interpolateProvider.startSymbol('{[{');
  $interpolateProvider.endSymbol('}]}');
  $httpProvider.defaults.xsrfCookieName = 'csrftoken';
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
});
