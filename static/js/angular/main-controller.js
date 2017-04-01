angular.module('glaucoma')
    .controller('MainController', ['$scope', function ($scope) {
            /**
             * @ngdoc controller
             * @name MainController
             * @requires $scope
             */

            // myvar can now be used in the HTML
            // {[ myvar ]} will display "Hello World"
            $scope.myvar = "Hello World";
        }]);
