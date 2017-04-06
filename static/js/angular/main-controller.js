(function () {
    'use strict';
    angular.module('glaucoma')
        .controller('MainController', ['$scope', '$http', function ($scope, $http) {

            $scope.algos = [
                {'key':'MD',
                 'label': 'MD',
                  'rank': 'md_rank'
                },
                {'key':'VFI',
                 'label': 'VFI',
                  'rank': 'vfi_rank'
                },
                {'key':'CIGTS',
                 'label': 'CIGTS'
                },
                {'key':'AGIS',
                 'label': 'AGIS'
                },
                {'key':'PLR',
                 'label': 'PLR'
                },
                {'key':'POPLR',
                 'label': 'POPLR'
                },
                {'key':'RandomForest',
                 'label': 'Random Forest'
                },
                {'key':'Truth',
                 'label': 'Truth'
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

                    _.each(_.range($scope.num_vfs), function (index) {
                        $('#chart' + index).remove()
                    });

                    $scope.num_vfs = $scope.data.data.length;
                    _.forEach($scope.data.data, function (value, index) {
                        var element = document.createElement('div');
                        element.setAttribute("id", "chart" + index);
                        document.getElementById("charts").appendChild(element);
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
                    data_type: "sensitivity",
                    show: true
                },
                {
                    name: "Total Deviation",
                    data_type: "td",
                    show: true
                },
                {
                    name: "Pattern Deviation",
                    data_type: "pd",
                    show: true
                },
                {
                    name: "Total Deviation Prob",
                    data_type: "tdp",
                    show: false
                },
                {
                    name: "Pattern Deviation Prob",
                    data_type: "pdp",
                    show: false
                }
            ];

            $scope.borderColorMap = {
                'td': 'tdp',
                'pd': 'pdp'
            };

            $scope.getViews = function () {
                return _.filter($scope.views, function (view) {
                    return view.show;
                })
            };

            $scope.selectedView = $scope.views[2];
            $scope.showValuesOnHeatMap = false;
            var svg,
                scale,
                legendItemWidth = 18,
                legendItemSpacing = 6,
                totalwidth = 500,
                height = 340,
                marginLeft = 5,
                marginTop = 5,
                gridSize = 34, transitionDuration = 25,
                colors = ["#343434", "#696969", "#A9A9A9", "#C0C0C0", "#DCDCDC", "#F5F5F5"];

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
                        .attr('x', totalwidth - 160)
                        .attr('y', y)
                        .text(text);
                };

                addText(height - 130, metadata["nmeas"] + ' ' + metadata["yearsfollowed"]);
                addText(height - 110, metadata["md"]);
                addText(height - 90, metadata["psd"]);
                addText(height - 70, metadata["vfi"]);

                var rect_group = svg.append("g");
                rect_group.selectAll("rect")
                    .data(data)
                    .enter()
                    .append("rect")
                    .attr("x", function (d) {
                        return (d.x) * gridSize + marginLeft;
                    })
                    .attr("y", function (d) {
                        return d.y * gridSize + marginTop;
                    })
                    .attr("width", gridSize)
                    .attr("height", gridSize)
                    .transition().duration(function (d, i) {
                        return i * transitionDuration;
                    })
                    .style("fill", function (d) {
                        if (dataType == 'sensitivity') {
                            return "transparent"
                        }
                        return colors[Math.floor(scale(d[dataType]))];
                    })
                    .style("fill-opacity", 1.0);

                var border_rect_group = svg.append("g");
                border_rect_group.selectAll("rect")
                    .data(data)
                    .enter()
                    .append("rect")
                    .attr("x", function (d) {
                        return (d.x) * gridSize + marginLeft;
                    })
                    .attr("y", function (d) {
                        return d.y * gridSize + marginTop;
                    })
                    .attr("width", gridSize)
                    .attr("height", gridSize)
                    .attr("class", "bordered")
                    .attr('stroke', function (d) {
                        if (!$scope.borderColorMap[dataType]) {
                            return "transparent"
                        }
                        var data_point = d[$scope.borderColorMap[dataType]];
                        switch (data_point) {
                            case  0.005: return "rgb(231, 76, 60)";
                            case   0.01: return "rgb(255, 145, 134)";
                            case   0.02: return "rgb(255, 145, 134)";
                            case   0.05: return "rgb(255, 145, 134)";
                            case      1: return 'transparent';
                            default: return "transparent"
                        }
                    })
                    .attr('stroke-linecap', 'butt')
                    .attr('stroke-width', "3")
                    .style("fill", "transparent")
                    .style("fill-opacity", 0.0);

                showTextElements(data);
                $scope.setTextVisibility();

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
                    })
                    .style("fill-opacity", 1.0);

                legend.append('text')
                    .attr('x', legendItemWidth + legendItemSpacing)
                    .attr('y', legendItemWidth - legendItemSpacing)
                    .text(function (d) {
                        var start = Math.round(scale.invert(d)),
                            end = Math.round(scale.invert(d + 1)),
                            label;
                        if (start === end) {
                            label = start
                        } else if (start == min) {
                            label = "Below " + end
                        } else if (end == max) {
                            label = "Above " + start
                        } else {
                            label = end
                        }
                        return label;
                    });
            };

            $scope.setTextVisibility = function () {
                if ($scope.selectedView.data_type != 'sensitivity') {
                    if ($scope.showValuesOnHeatMap) {
                        $('text.label-text').removeClass('hidden');
                    } else {
                        $('text.label-text').addClass('hidden');
                    }
                }
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
                        return (d.x) * gridSize + gridSize * 0.5 + marginLeft;
                    })
                    .attr("y", function (d) {
                        return d.y * gridSize + gridSize * 0.66 + marginTop;
                    })
                    .style("text-anchor", "middle")
                    .transition().duration(function (d, i) {
                        return 100 + i * transitionDuration;
                    })
                    .style("fill", function (d) {
                        var dataType = $scope.selectedView.data_type;
                        if (Math.floor(scale(d[dataType])) == 0 && $scope.selectedView.data_type != 'sensitivity') {
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
