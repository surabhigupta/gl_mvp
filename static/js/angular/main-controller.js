(function () {
    'use strict';
    angular.module('glaucoma')
        .controller('MainController', ['$scope', '$http', function ($scope, $http) {

            $scope.algos = [
                {'key':'md_label',
                 'label': 'MD'
                },
                {'key':'vfi_label',
                 'label': 'VFI'
                },
                {'key':'cigts_label',
                 'label': 'CIGTS'
                },
                {'key':'agis_label',
                 'label': 'AGIS'
                },
                {'key':'plr_label',
                 'label': 'PLR'
                },
                {'key':'poplr_label',
                 'label': 'POPLR'
                },
                {'key':'true_label',
                 'label': 'True Label'
                }
            ];

            $http.get("/patients").then(function (response) {
                $scope.patients = response.data.data;
                $scope.selectedPatient = $scope.patients[0].id + '_' + $scope.patients[0].eye;

                $scope.getPatientData(1);
            });

            $scope.getPatientData = function (first) {
                $http.get("/vf/" + $scope.selectedPatient).then(function (response) {
                    $scope.data = response.data;
                    _.forEach($scope.data.data, function (value, index) {
                        if (first) {
                            var element = document.createElement('div');
                            element.setAttribute("id", "chart" + index);
                            document.getElementById("charts").appendChild(element);
                        }
                        $scope.drawChart(index, value, $scope.data.metadata[index]);
                    });
                });
                $scope.getLabels()
            };

            $scope.getLabels = function() {
                $http.get("/labels/" + $scope.selectedPatient).then(function (response) {
                    $scope.labels = response.data;
                });
            };

            $scope.views = [
                {
                    name: "Sensitivity",
                    data_type: "sensitivity"
                },
                {
                    name: "Total Deviation",
                    data_type: "td"
                },
                {
                    name: "Pattern Deviation",
                    data_type: "pd"
                }
            ];
            $scope.selectedView = $scope.views[0];
            $scope.showValuesOnHeatMap = true;
            var svg,
                scale,
                legendItemWidth = 18,
                legendItemSpacing = 6,
                totalwidth = 500,
                height = 340,
                gridSize = 40, transitionDuration = 25,
                colors = ["#000000", "#696969", "#808080", "#A9A9A9", "#C0C0C0", "#D3D3D3", "#DCDCDC", "#F5F5F5"]

            $scope.drawChart = function (id, data, metadata) {
                var chartName = "#chart" + id;
                var dataType = $scope.selectedView.data_type;
                var title = $scope.selectedView.name;
                d3.select(chartName).selectAll("svg").remove();

                svg = d3.select(chartName).append("svg")
                    .attr("width", totalwidth)
                    .attr("height", height);

                var min = d3.min(data, function (d) {
                    return d[dataType];
                });
                var max = d3.max(data, function (d) {
                    return d[dataType];
                });
                scale = d3.scale.linear()
                    .domain([min, max])
                    .range([0, colors.length - 1]);

                var addText = function (y, text) {
                    svg.append('text')
                        .attr('x', totalwidth - 150)
                        .attr('y', y)
                        .text(text);
                };

                addText(height - 80, metadata["nmeas"] + ' ' + metadata["yearsfollowed"]);
                addText(height - 60, metadata["md"]);
                addText(height - 40, metadata["psd"]);
                addText(height - 20, metadata["vfi"]);

                var rect_group = svg.append("g");
                rect_group.selectAll("rect")
                    .data(data)
                    .enter()
                    .append("rect")
                    .attr("x", function (d) {
                        return (d.x) * gridSize;
                    })
                    .attr("y", function (d) {
                        return d.y * gridSize;
                    })
                    .attr("width", gridSize)
                    .attr("height", gridSize)
                    .attr("class", "bordered")
                    .transition().duration(function (d, i) {
                        return i * transitionDuration;
                    })
                    .style("fill", function (d) {
                        return colors[Math.floor(scale(d[dataType]))];
                    })
                    .style("fill-opacity", 0.7);

                if ($scope.showValuesOnHeatMap) {
                    showTextElements(data);
                }

                var legend_group =
                    svg.append("g")
                        .attr('transform', 'translate(' + gridSize * 10 + ', ' + 0 + ')');
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
                        } else if (start == min) {
                            label = "Below " + end
                        } else if (end == max) {
                            label = "Above " + end
                        }
                        else {
                            label = end
                        }
                        return label;
                    });
            };

            $scope.toggleTextVisibility = function () {
                $('text.label-text').toggleClass('hidden');
            };

            var showTextElements = function (data) {
                svg.selectAll(".label-text").remove();
                var label_group = svg.append("g");
                label_group.selectAll(".label-text")
                    .data(data)
                    .enter()
                    .append("text")
                    .text(function (d) {
                        return d[$scope.selectedView.data_type];
                    })
                    .attr("class", "label-text")
                    .attr("x", function (d, i) {
                        return (d.x) * gridSize + gridSize * 0.5;
                    })
                    .attr("y", function (d) {
                        return d.y * gridSize + gridSize * 0.66;
                    })
                    .style("text-anchor", "middle")
                    .transition().duration(function (d, i) {
                        return 100 + i * transitionDuration;
                    })
                    .style("fill", function (d) {
                        var dataType = $scope.selectedView.data_type;
                        if (Math.floor(scale(d[dataType])) == 0) {
                            return "#ffffff"
                        }
                        return "#000000"
                    });
            };

            $scope.refreshCharts = function () {
                _.forEach($scope.data.data, function (value, index) {
                    $scope.drawChart(index, value, $scope.data.metadata[index]);
                });
            };

        }]);
}());
