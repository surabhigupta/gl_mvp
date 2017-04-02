(function () {
    'use strict';
    angular.module('glaucoma')
        .controller('MainController', ['$scope', '$http', function ($scope, $http) {
            $scope.datasets = [
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
            $scope.selectedDataset = $scope.datasets[0];
            $scope.showCursorText = false;
            $scope.hoverText = "";
            $scope.showValuesOnHeatMap = false;
            var svg,
                scale,
                legendItemWidth = 18,
                legendItemSpacing = 6,
                totalwidth = 700,
                height = 300,
                gridSize = 32, transitionDuration = 25,
                colors = ["#edf8b1", "#c7e9b4", "#7fcdbb", "#41b6c4", "#1d91c0", "#225ea8", "#253494", "#081d58"],
                textColors = ["#41b6c4", "#7fcdbb", "#c7e9b4", "#edf8b1", "#081d58", "#253494", "#225ea8", "#1d91c0"],
                days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

            $scope.drawChart = function () {
                var dataType = $scope.selectedDataset.data_type;
                var title = $scope.selectedDataset.name;
                d3.select("#chart").selectAll("svg").remove();

                svg = d3.select("#chart").append("svg")
                    .attr("width", totalwidth)
                    .attr("height", height)

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
                        return (d.day - 1) * gridSize;
                    })
                    .attr("y", function (d) {
                        return d.hour * gridSize;
                    })
                    .attr("rx", 4)
                    .attr("ry", 4)
                    .attr("width", gridSize)
                    .attr("height", gridSize)
                    .attr("class", "bordered")
                    .on('mouseover', function (d) {
                        $scope.hoverText = $scope.getCursorText(d);
                        //$scope.$apply(function () {
                        //})
                    })
                    .on('mouseout', function (d) {
                        $scope.$apply(function () {
                            $scope.hoverText = ""
                        });
                    })
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
                        return d[$scope.selectedDataset.data_type];
                    })
                    .attr("class", "label-text")
                    .attr("x", function (d, i) {
                        return d.day * gridSize + gridSize * 5 / 6;
                    })
                    .attr("y", function (d) {
                        return d.hour * gridSize + gridSize * 5 / 6;
                    })
                    .style("text-anchor", "end")
                    .transition().duration(function (d, i) {
                        return 100 + i * transitionDuration;
                    })
                    .style("fill", function (d) {
                        var colorIndex = Math.floor(scale(d[$scope.selectedDataset.data_type]));
                        return textColors[textColors.length - colorIndex];
                    });
            };

            $http.get("/dummy").then(function (response) {
                $scope.data = response.data.data;
                $scope.drawChart();
            });

            $scope.getCursorText = function (d) {
                var hoverText = "";
                for (var i = 0; i < $scope.datasets.length; i++) {
                    var type = $scope.datasets[i].data_type;
                    if (d.hasOwnProperty(type)) {
                        hoverText += $scope.datasets[i].name + ": " + d[type] + '<br>';
                    }
                }
                return hoverText;
            };

            $(document).mousemove(function (e) {
                $scope.showCursorText = true;
                var cpos = {top: e.pageY + 10, left: e.pageX + 10};
                $('#hover-text').offset(cpos);
            });

        }]);
}());
