(function () {
    'use strict';
    angular.module('glaucoma')
        .controller('MainController', ['$scope', '$http', function ($scope, $http) {
            $scope.views = [
                {
                    name: "Insertions",
                    data_type: "insertions"
                },
                {
                    name: "Deletions",
                    data_type: "deletions"
                },
                {
                    name: "Files Changed",
                    data_type: "files_changed"
                },
                {
                    name: "Commits",
                    data_type: "commits"
                }
            ];
            $scope.selectedView = $scope.views[0];
            $scope.showValuesOnHeatMap = false;
            var svg,
                scale,
                legendItemWidth = 18,
                legendItemSpacing = 6,
                totalwidth = 700,
                height = 300,
                gridSize = 40, transitionDuration = 25,
                colors = ["#edf8b1", "#c7e9b4", "#7fcdbb", "#41b6c4", "#1d91c0", "#225ea8", "#253494", "#081d58"],
                textColors = ["#41b6c4", "#7fcdbb", "#c7e9b4", "#edf8b1", "#081d58", "#253494", "#225ea8", "#1d91c0"];

            $scope.drawChart = function () {
                var dataType = $scope.selectedView.data_type;
                var title = $scope.selectedView.name;
                d3.select("#chart").selectAll("svg").remove();

                svg = d3.select("#chart").append("svg")
                    .attr("width", totalwidth)
                    .attr("height", height);

                var min = d3.min($scope.data, function (d) {
                    return d[dataType];
                });
                var max = d3.max($scope.data, function (d) {
                    return d[dataType];
                });
                scale = d3.scale.pow().exponent(.2)
                    .domain([min, max])
                    .range([0, Math.min(max, colors.length - 1)]);

                var rect_group = svg.append("g");
                rect_group.selectAll("rect")
                    .data($scope.data)
                    .enter()
                    .append("rect")
                    .attr("x", function (d) {
                        return (d.day) * gridSize;
                    })
                    .attr("y", function (d) {
                        return d.hour * gridSize;
                    })
                    .attr("rx", 2)
                    .attr("ry", 2)
                    .attr("width", gridSize)
                    .attr("height", gridSize)
                    .attr("class", "bordered")
                    .transition().duration(function (d, i) {
                        return i * transitionDuration;
                    })
                    .style("fill", function (d) {
                        return colors[Math.floor(scale(d[dataType]))];
                    })
                    .style("fill-opacity", 0.8);

                if ($scope.showValuesOnHeatMap) {
                    showTextElements();
                }

                var legend_group =
                    svg.append("g")
                        .attr('transform', 'translate(' + gridSize * 9 + ', ' + 0 + ')');
                var legend = legend_group.selectAll('.legend')
                    .data(d3.range(scale.range()[0], scale.range()[1], 1))
                    .enter()
                    .append('g')
                    .attr('transform', function (d, i) {
                        var width = legendItemWidth + legendItemSpacing;
                        var y = i * width;
                        return 'translate(' + 0 + ',' + y + ')';
                    });

                legend.append('rect')
                    .attr('width', legendItemWidth)
                    .attr('height', legendItemWidth)
                    .attr('class', 'legend')
                    .style('fill', function (d) {
                        return colors[d];
                    });

                legend.append('text')
                    .attr('x', legendItemWidth + legendItemSpacing)
                    .attr('y', legendItemWidth - legendItemSpacing)
                    .text(function (d) {
                        var start = Math.ceil(scale.invert(d)),
                            end = Math.ceil(scale.invert(d + 1)),
                            label;
                        if (start === end) {
                            label = start
                        } else {
                            label = start + " - " + end
                        }
                        return label;
                    });
            };

            $scope.toggleTextVisibility = function () {
                if ($scope.showValuesOnHeatMap) {
                    showTextElements();
                } else {
                    svg.selectAll(".label-text").remove()
                }
            };

            var showTextElements = function () {
                svg.selectAll(".label-text").remove();
                var label_group = svg.append("g");
                label_group.selectAll(".label-text")
                    .data($scope.data)
                    .enter()
                    .append("text")
                    .text(function (d) {
                        return d[$scope.selectedView.data_type];
                    })
                    .attr("class", "label-text")
                    .attr("x", function (d, i) {
                        return (d.day) * gridSize + gridSize*0.5;
                    })
                    .attr("y", function (d) {
                        return d.hour * gridSize + gridSize*0.66;
                    })
                    .style("text-anchor", "middle")
                    .transition().duration(function (d, i) {
                        return 100 + i * transitionDuration;
                    })
                    .style("fill", function (d) {
                        var colorIndex = Math.floor(scale(d[$scope.selectedView.data_type]));
                        return textColors[textColors.length - colorIndex];
                    });
            };

            $http.get("/dummy").then(function (response) {
                $scope.data = response.data.data;
                $scope.drawChart();
            });

        }]);
}());
