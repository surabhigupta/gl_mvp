(function () {
    'use strict';
    angular.module('glaucoma', ['ngRoute'])
        .config(['$logProvider', function ($logProvider) {
            $logProvider.debugEnabled(true);
        }])
        .config(['$interpolateProvider', '$locationProvider', '$routeProvider',
            function ($interpolateProvider, $locationProvider, $routeProvider) {
                /**
                 * Configuring Angular to use different binding tags to avoid a conflict with Jinja.
                 */
                $interpolateProvider.startSymbol('{[');
                $interpolateProvider.endSymbol(']}');

                $routeProvider
                .when('/', {
                    templateUrl: 'static/templates/index.html',
                    controller: 'MainController'
                })
                .otherwise({redirectTo: '/'});

                $locationProvider.html5Mode({
                    enabled: true,
                    requireBase: false
                });
            }])
}());
