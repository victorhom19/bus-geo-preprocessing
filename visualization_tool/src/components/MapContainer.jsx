import './MapContainer.css'

import { observer } from 'mobx-react-lite'
import { Feature, Map, Overlay, View } from 'ol';
import TileLayer from 'ol/layer/Tile';
import VectorLayer from 'ol/layer/Vector';

import OSM from 'ol/source/OSM';
import VectorSource from 'ol/source/Vector';
import { useEffect, useRef, useState } from 'react';
import AppStore, { DisplayInfo, Mode, Source } from '../store/AppStore';
import Draw, { createBox } from 'ol/interaction/Draw'
import { LineString, Point } from 'ol/geom';
import {Circle, Fill, RegularShape, Stroke, Style} from 'ol/style.js';
import Layer from 'ol/layer/Layer';
import { palette, capitalizeString, colorLerp } from '../../utils';
import { toJS } from 'mobx';
import RequestDataForm from './RequestDataForm';


class StopsAndRoutesStyles {

    static _syncedStopStyle = new Style({
        image: new Circle({
            fill: new Fill({color: 'white'}),
            stroke: new Stroke({color: 'rgb(64, 175, 69)', width: 10}),
            radius: 25
        })
    })

    static syncedStopStyle = (feature, resolution) => {
        this._syncedStopStyle.getImage().setScale(1 / 3 / Math.pow(resolution, 1/6));
        return this._syncedStopStyle;
    }

    static _unsyncedStopStyle = new Style({
        image: new Circle({
            fill: new Fill({color: 'white'}),
            stroke: new Stroke({color: 'rgb(255, 119, 0)', width: 10}),
            radius: 25
        })
    })

    static unsyncedStopStyle = (feature, resolution) => {
        this._unsyncedStopStyle.getImage().setScale(1 / 3 / Math.pow(resolution, 1/6));
        return this._unsyncedStopStyle;
    }

    static _syncedRouteGeometryStyle = new Style({
        stroke: new Stroke({
            color: 'rgb(0, 170, 9)',
            width: 4
        })
    })

    static syncedRouteGeometryStyle = (feature, resolution) => {
        this._syncedRouteGeometryStyle.getStroke().setWidth(4 * 1 / Math.pow(resolution, 1/6));
        return this._syncedRouteGeometryStyle;
    }

    static _unsyncedRouteGeometryStyle = new Style({
        stroke: new Stroke({
            color: 'rgb(255, 119, 0)',
            width: 4
        })
    })

    static unsyncedRouteGeometryStyle = (feature, resolution) => {
        this._unsyncedRouteGeometryStyle.getStroke().setWidth(4 * 1 / Math.pow(resolution, 1/6));
        return this._unsyncedRouteGeometryStyle;
    }

    static _syncedStopPositionStyle = new Style({
        image: new RegularShape({
            fill: new Fill({color: 'white'}),
            stroke: new Stroke({color: 'rgb(0, 170, 9)', width: 4}),
            radius: 15,
            points: 4,
            angle: Math.PI / 4
        })
    })

    static syncedStopPositionStyle = (feature, resolution) => {
        this._syncedStopPositionStyle.getImage().setScale(1 / 2 / Math.pow(resolution, 1/6));
        return this._syncedStopPositionStyle;
    }

    static _unsyncedStopPositionStyle = new Style({
        image: new RegularShape({
            fill: new Fill({color: 'white'}),
            stroke: new Stroke({color: 'rgb(255, 119, 0)', width: 4}),
            radius: 15,
            points: 4,
            angle: Math.PI / 4
        })
    })

    static unsyncedStopPositionStyle = (feature, resolution) => {
        this._unsyncedStopPositionStyle.getImage().setScale(1 / 2 / Math.pow(resolution, 1/6));
        return this._unsyncedStopPositionStyle;
    }


    static obstacleStyle = new Style({})

}

class TrafficFlowStyles {

    static _stopStyle = new Style({
        image: new Circle({
            fill: new Fill({color: 'white'}),
            stroke: new Stroke({color: 'rgb(118, 118, 118)', width: 8}),
            radius: 20
        })
    })

    static stopStyle = (feature, resolution) => {
        this._stopStyle.getImage().setScale(1 / 3 / Math.pow(resolution, 1/6));
        return this._stopStyle;
    }

    static _stopPositionStyle = new Style({
        image: new RegularShape({
            fill: new Fill({color: 'white'}),
            stroke: new Stroke({color: 'rgb(118, 118, 118)', width: 4}),
            radius: 15,
            points: 4,
            angle: Math.PI / 4
        })
    })

    static stopPositionStyle = (feature, resolution) => {
        this._stopPositionStyle.getImage().setScale(1 / 2 / Math.pow(resolution, 1/6));
        return this._stopPositionStyle;
    }

    static _obstacleStyle = new Style({
        image: new RegularShape({
            fill: new Fill({color: 'white'}),
            stroke: new Stroke({color: 'rgb(246, 92, 20)', width: 3}),
            radius: 8,
            points: 3
        })
    })

    static obstacleStyle = (feature, resolution) => {
        this._obstacleStyle.getImage().setScale(1 / Math.pow(resolution, 1/6));
        return this._obstacleStyle;
    }

    static routeGeometryStyle = (feature, resolution) => {
        let color = 'rgb(118, 118, 118)'
        if (feature.getProperties().speed) {
            const ratio = Math.min(1.0, feature.getProperties().speed / 60)
            if (ratio < 0.5) {
                color = colorLerp("#aa0000", "#aaaa00", 2 * ratio)
            } else {
                color = colorLerp("#aaaa00", "#00aa00", 2 * (ratio - 0.5))
            }
        }
        const style = new Style({
            stroke: new Stroke({
                color: color,
                width: 4
            })
        })
        style.getStroke().setWidth(4 * 1 / Math.pow(resolution, 1/6))
        return style;
    }

}

class StopsClusteringStyles {

    // ----- STOPS CLUSTERING -----

    static clusteredStyles = null

    static _nonClusteredStopStyle = new Style({
        image: new Circle({
            fill: new Fill({color: 'white'}),
            stroke: new Stroke({color: 'rgb(118, 118, 118)', width: 2}),
            radius: 8
        })
    })

    static nonClusteredStopStyle = (feature, resolution) => {
        this._nonClusteredStopStyle.getImage().setScale(1 / Math.pow(resolution, 1/8));
        return this._nonClusteredStopStyle;
    }

    static generateStyles(clustersCount) {
        StopsClusteringStyles.clusteredStyles = []

        const colors = palette(clustersCount)

        for (let i = 0; i < clustersCount; i++) {
            StopsClusteringStyles.clusteredStyles.push((feature, resolution) => {
                const style = new Style({
                    image: new Circle({
                        fill: new Fill({color: colors[i]}),
                        stroke: new Stroke({color: 'rgb(53, 53, 53)', width: 1}),
                        radius: 8
                    })
                })
                style.getImage().setScale(1 / Math.pow(resolution, 1/8));
                return style
            })
        }
    }

}


class MapController {

    DEFAULT_VIEW = new View({center: [37.5661937,55.7465035], zoom: 10})
    //DEFAULT_VIEW = new View({center: [30.3820682,59.9796189], zoom: 10})

    HIDDEN_STYLE = new Style({})

    createMap(mapElementRef, popupRef) {
        
        this.popupRef = popupRef

        // Instantiating map layers
        this.rasterLayer = new TileLayer({preload: Infinity, source: new OSM()})
        this.bboxLayer = new VectorLayer({source: new VectorSource({wrapX: false})})
        this.stopsAndRoutesLayer = new VectorLayer({source: new VectorSource({wrapX: false})})
        this.trafficFlowLayer = new VectorLayer({source: new VectorSource({wrapX: false})})
        this.stopsClusteringLayer = new VectorLayer({source: new VectorSource({wrapX: false})})
        
        // Grouping Layers
        this.activeLayer = this.stopsAndRoutesLayer
        this.allLayers = [this.bboxLayer, this.stopsAndRoutesLayer, this.trafficFlowLayer, this.stopsClusteringLayer]
        this.featureLayers = [this.stopsAndRoutesLayer, this.trafficFlowLayer, this.stopsClusteringLayer]
        
        // Binding popup overlay
        this.overlay = new Overlay({element: this.popupRef.current});

        // Creating Map object
        this.map = new Map({
            target: mapElementRef.current,
            layers: [this.rasterLayer, this.bboxLayer, this.stopsAndRoutesLayer, this.trafficFlowLayer, this.stopsClusteringLayer],
            view: this.DEFAULT_VIEW,
            controls: [],  // Disable OL default controls
            overlays: [this.overlay]
        })

        this.map.on('click', (e) => {
            for (const feature of this.map.getFeaturesAtPixel(e.pixel)) {
                const mapEntity = feature.getProperties().associatedMapEntity
                AppStore.setSelectedMapEntity(mapEntity)
                break
            }
        })

        this.map.on('pointermove', e => {
            
            let hit = false

            for (const feature of this.map.getFeaturesAtPixel(e.pixel)) {
                if (feature.getProperties().visible) {
                    const pixelCoordinates = this.map.getPixelFromCoordinate(e.coordinate)
                    const pixelCoordinatesWithOffset = [pixelCoordinates[0] + 20, pixelCoordinates[1]]
                    const coordinatesWithOffset = this.map.getCoordinateFromPixel(pixelCoordinatesWithOffset)

                    this.popupRef.current.innerHTML = capitalizeString(feature.getProperties().hoverInfo);
                    this.overlay.setPosition(coordinatesWithOffset);

                    hit = true
                    break
                }
            }

            if (!hit) this.overlay.setPosition(null);
        })

    }

    // MAP FUNCTIONS

    focusOnLayer(layer) {
        this.featureLayers.forEach(f => f.setVisible(false))
        this.activeLayer = layer
        this.activeLayer.setVisible(true)
    }

    showFeature(feature) {
        if (!feature.getProperties().visible) {
            feature.setProperties({visible: true})
            feature.setStyle(feature.getProperties().visibleStyle)
        }
    }

    hideFeature(feature) {
        if (feature.getProperties().visible) {
            feature.setProperties({visible: false})
            feature.setStyle(this.HIDDEN_STYLE)
        }
    }

    showAllFeatures() {
        this.activeLayer.getSource().forEachFeature(f => this.showFeature(f))
    }

    hideAllFeatures() {
        this.activeLayer.getSource().forEachFeature(f => this.hideFeature(f))
    }

    highlightMapEntity(mapEntity) {
        this.hideAllFeatures()
        const features = this.activeLayer.getSource().getFeatures().filter(f => f.getProperties().associatedMapEntity.id === mapEntity.id)
        features.forEach(f => this.showFeature(f))
    }

    moveMapToMapEntity(mapEntity) {
        const params = {
            maxZoom: Math.max(16, this.map.getView().getZoom()),
            padding: [100, 100, 100, 100]
        }
        this.map.getView().fit(mapEntity.extent, params)
    }

    focusOnMapEntity(mapEntity) {
        this.hideAllFeatures()
        this.highlightMapEntity(mapEntity)
        this.moveMapToMapEntity(mapEntity)
    }


    // STOPS AND ROUTES

    renderStops(stops) {
        const stopsAsFeatures = []
        stops.forEach(stop => {
            const geometry = new Point([stop.lon, stop.lat])
            stop.extent = geometry.getExtent()
            const style = stop.source === Source.LOCAL.apiCode ? StopsAndRoutesStyles.syncedStopStyle 
                                                               : StopsAndRoutesStyles.unsyncedStopStyle
            const feature = new Feature({
                geometry: geometry,
                visible: true,
                associatedMapEntity: stop,
                hoverInfo: stop.name,
                visibleStyle: style,
            })
            feature.setStyle(style)
            stopsAsFeatures.push(feature)
        })

        this.stopsAndRoutesLayer.getSource().addFeatures(stopsAsFeatures)
    }

    renderRoutes(routes) {
        
        const routesAsFeatures = []
        routes.forEach(route => {

            // Route geometry
            const routeGeometryGeometry = new LineString(route.geometry.map(g => [g.lon, g.lat]))
            route.extent = routeGeometryGeometry.getExtent()
            const routeGeometryStyle = route.source === Source.LOCAL.apiCode ? StopsAndRoutesStyles.syncedRouteGeometryStyle : StopsAndRoutesStyles.unsyncedRouteGeometryStyle
            const routeGeometryAsFeature = new Feature({
                geometry: routeGeometryGeometry,
                visible: true,
                associatedMapEntity: route,
                hoverInfo: route.name,
                visibleStyle: routeGeometryStyle,
            })
            routeGeometryAsFeature.setStyle(routeGeometryStyle)
                        
            // Route stop positions
            const routeStopPositionsAsFeatures = []
            route.geometry.filter(g => g.type === 'stop_position').forEach(stop_position => {
                const routeStopPositionStyle = route.source === Source.LOCAL.apiCode ? StopsAndRoutesStyles.syncedStopPositionStyle : StopsAndRoutesStyles.unsyncedStopPositionStyle
                const routeStopPositionAsFeature = new Feature({
                    geometry: new Point([stop_position.lon, stop_position.lat]),
                    visible: true,
                    associatedMapEntity: route,
                    hoverInfo: route.name,
                    visibleStyle: routeStopPositionStyle,
                })
                routeStopPositionAsFeature.setStyle(routeStopPositionStyle)
                routeStopPositionsAsFeatures.push(routeStopPositionAsFeature)
            })

            // Route stops
            const routeStopsAsFeatures = []
            route.stops.forEach(stop => {
                const routeStopStyle = stop.source === Source.LOCAL.apiCode ? StopsAndRoutesStyles.syncedStopStyle : StopsAndRoutesStyles.unsyncedStopStyle
                const routeStopAsFeature = new Feature({
                    geometry: new Point([stop.lon, stop.lat]),
                    visible: true,
                    associatedMapEntity: route,
                    hoverInfo: stop.name,
                    visibleStyle: routeStopStyle,
                })
                routeStopAsFeature.setStyle(routeStopStyle)
                routeStopsAsFeatures.push(routeStopAsFeature)
            })

            routesAsFeatures.push(routeGeometryAsFeature, ...routeStopPositionsAsFeatures, ...routeStopsAsFeatures)
        })
        
        this.stopsAndRoutesLayer.getSource().addFeatures(routesAsFeatures)
    }

    // TRAFFIC FLOW
    getObstacleRepresentationString(obstacleType) {
        switch (obstacleType) {
            case "traffic_signals":
                return "Светофор"
            case "crossing":
                return "Пешеходный переход"
            case "speedbump":
                return "Лежачий полицейский"
            case "roundabout":
                return "Въезд на круговое движение"
        }
    }

    routeWithoutTrafficAsFeatures(route) {
        // Route geometry
        const routeGeometryGeometry = new LineString(route.geometry.map(g => [g.lon, g.lat]))
        route.extent = routeGeometryGeometry.getExtent()
        const routeGeometryAsFeature = new Feature({
            geometry: routeGeometryGeometry,
            visible: true,
            associatedMapEntity: route,
            hoverInfo: route.name,
            visibleStyle: TrafficFlowStyles.routeGeometryStyle,
        })
        routeGeometryAsFeature.setStyle(TrafficFlowStyles.routeGeometryStyle)
                    
        // Route stop positions
        const routeStopPositionsAsFeatures = []
        route.geometry.filter(g => g.type === 'stop_position').forEach(stop_position => {
            const routeStopPositionAsFeature = new Feature({
                geometry: new Point([stop_position.lon, stop_position.lat]),
                visible: true,
                associatedMapEntity: route,
                hoverInfo: route.name,
                visibleStyle: TrafficFlowStyles.stopPositionStyle,
            })
            routeStopPositionAsFeature.setStyle(TrafficFlowStyles.stopPositionStyle)
            routeStopPositionsAsFeatures.push(routeStopPositionAsFeature)
        })

        // Route obstacles
        const routeObstaclesAsFeatures = []
        route.geometry.filter(g => g.type === 'obstacle').forEach(obstacle => {
            const routeObstacleAsFeature = new Feature({
                geometry: new Point([obstacle.lon, obstacle.lat]),
                visible: true,
                associatedMapEntity: route,
                hoverInfo: this.getObstacleRepresentationString(obstacle.obstacle_type),
                visibleStyle: TrafficFlowStyles.obstacleStyle,
            })
            routeObstacleAsFeature.setStyle(TrafficFlowStyles.obstacleStyle)
            routeObstaclesAsFeatures.push(routeObstacleAsFeature)
        })

        // Route stops
        const routeStopsAsFeatures = []
        route.stops.forEach(stop => {
            const routeStopAsFeature = new Feature({
                geometry: new Point([stop.lon, stop.lat]),
                visible: true,
                associatedMapEntity: route,
                hoverInfo: stop.name,
                visibleStyle: TrafficFlowStyles.stopStyle,
            })
            routeStopAsFeature.setStyle(TrafficFlowStyles.stopStyle)
            routeStopsAsFeatures.push(routeStopAsFeature)
        })

        return [routeGeometryAsFeature, ...routeStopPositionsAsFeatures, ...routeObstaclesAsFeatures, 
                ...routeStopsAsFeatures]
    }

    routeWithTrafficAsFeatures(route, routeTrafficFlow) {

        const routeGeometryGeometry = new LineString(route.geometry.map(g => [g.lon, g.lat]))
        route.extent = routeGeometryGeometry.getExtent()

        const createSegmentFeature = (lastSpeed, pointsBuffer, route) => {
            let segmentStyle = TrafficFlowStyles.routeGeometryStyle

            // Create and add line segment
            const routeSegmentFeature = new Feature({
                geometry: new LineString(pointsBuffer),
                visible: true,
                associatedMapEntity: route,
                hoverInfo: `${lastSpeed.toFixed(2)} км/ч`,
                visibleStyle: segmentStyle,
                speed: lastSpeed
            })
            routeSegmentFeature.setStyle(segmentStyle)

            return routeSegmentFeature
        }

        let lastSpeed = null

        const routeGeometryAsFeatures = []
        let pointsBuffer = []

        let stopCursor = 0

        for (let i = 0; i < route.geometry.length - 1; i++) {
            
            const segmentSpeed = routeTrafficFlow[stopCursor]
            const pointFrom = route.geometry[i]
            const pointTo = route.geometry[i+1]

            if (pointFrom.type === 'stop_position' && route.final_stop_order && route.final_stop_order === stopCursor) {
                pointsBuffer.push([pointFrom.lon, pointFrom.lat])
                lastSpeed = segmentSpeed
                continue
            }

            if (i === 0) {
                pointsBuffer.push([pointFrom.lon, pointFrom.lat])
                lastSpeed = segmentSpeed
            }

            if (segmentSpeed === lastSpeed) {
                pointsBuffer.push([pointTo.lon, pointTo.lat])
            } else {
                const routeSegmentFeature = createSegmentFeature(lastSpeed, pointsBuffer, route)
                routeGeometryAsFeatures.push(routeSegmentFeature)

                pointsBuffer = [[pointFrom.lon, pointFrom.lat], [pointTo.lon, pointTo.lat]]
                lastSpeed = segmentSpeed
            }

            if (pointTo.type === "stop_position") {
                stopCursor++
            }
        }

        const routeSegmentFeature = createSegmentFeature(lastSpeed, pointsBuffer, route)
        routeGeometryAsFeatures.push(routeSegmentFeature)

        // Route stop positions
        const routeStopPositionsAsFeatures = []
        route.geometry.filter(g => g.type === 'stop_position').forEach(stop_position => {
            const routeStopPositionAsFeature = new Feature({
                geometry: new Point([stop_position.lon, stop_position.lat]),
                visible: true,
                associatedMapEntity: route,
                hoverInfo: route.name,
                visibleStyle: TrafficFlowStyles.stopPositionStyle,
            })
            routeStopPositionAsFeature.setStyle(TrafficFlowStyles.stopPositionStyle)
            routeStopPositionsAsFeatures.push(routeStopPositionAsFeature)
        })

        // Route obstacles
        const routeObstaclesAsFeatures = []
        route.geometry.filter(g => g.type === 'obstacle').forEach(obstacle => {
            const routeObstacleAsFeature = new Feature({
                geometry: new Point([obstacle.lon, obstacle.lat]),
                visible: true,
                associatedMapEntity: route,
                hoverInfo: this.getObstacleRepresentationString(obstacle.obstacle_type),
                visibleStyle: TrafficFlowStyles.obstacleStyle,
            })
            routeObstacleAsFeature.setStyle(TrafficFlowStyles.obstacleStyle)
            routeObstaclesAsFeatures.push(routeObstacleAsFeature)
        })

        // Route stops
        const routeStopsAsFeatures = []
        route.stops.forEach(stop => {
            const routeStopAsFeature = new Feature({
                geometry: new Point([stop.lon, stop.lat]),
                visible: true,
                associatedMapEntity: route,
                hoverInfo: stop.name,
                visibleStyle: TrafficFlowStyles.stopStyle,
            })
            routeStopAsFeature.setStyle(TrafficFlowStyles.stopStyle)
            routeStopsAsFeatures.push(routeStopAsFeature)
        })

        return [...routeGeometryAsFeatures, ...routeStopPositionsAsFeatures, ...routeObstaclesAsFeatures, 
                ...routeStopsAsFeatures]

    } 

    renderTraffic(routes, trafficFlow) {

        const routesAsFeatures = []
        routes.forEach(route => {
            const routeTrafficFlow = trafficFlow[route.id]
            if (routeTrafficFlow) {
                routesAsFeatures.push(...this.routeWithTrafficAsFeatures(route, routeTrafficFlow))
            } else {
                routesAsFeatures.push(...this.routeWithoutTrafficAsFeatures(route))
            }
        })

        this.trafficFlowLayer.getSource().addFeatures(routesAsFeatures)
    }

    // STOPS CLUSTERING
    renderReferenceStops(referenceStops) {
        const N = 1
        const referenceStopsAsFeatures = []
        referenceStops.forEach((stop, i) => {
            if (i % N === 0) {
                const geometry = new Point([stop.lon, stop.lat])
                stop.extent = geometry.getExtent()
                const style = StopsClusteringStyles.nonClusteredStopStyle
                const feature = new Feature({
                    geometry: geometry,
                    visible: true,
                    hoverInfo: stop.name,
                    visibleStyle: style,
                    associatedMapEntity: stop
                })
                feature.setStyle(style)
                referenceStopsAsFeatures.push(feature)
            }
            
        })

        this.stopsClusteringLayer.getSource().addFeatures(referenceStopsAsFeatures)
    }

    renderClusteredReferenceStops(clusteredReferenceStops) {
        const N = 1
        const clusteredReferenceStopsAsFeatures = []
        clusteredReferenceStops.forEach((stop, i) => {
            if (i % N === 0) {
                const geometry = new Point([stop.lon, stop.lat])
                stop.extent = geometry.getExtent()
                const style = StopsClusteringStyles.clusteredStyles[stop.cluster_index]
                const feature = new Feature({
                    geometry: geometry,
                    visible: true,
                    hoverInfo: stop.name,
                    visibleStyle: style,
                    associatedMapEntity: stop
                })
                feature.setStyle(style)
                clusteredReferenceStopsAsFeatures.push(feature)
            }
        })

        this.stopsClusteringLayer.getSource().addFeatures(clusteredReferenceStopsAsFeatures)
    }

}

const MapContainer = observer(() => {

    const mapElementRef = useRef(null);
    const popupRef = useRef(null)

    const [isEditingBBox, setIsEditingBBox] = useState(false);

    const [mapController] = useState(() => new MapController())

    // Init Map
    useEffect(() => {
        mapController.createMap(mapElementRef, popupRef) 
        return () => mapController.map.setTarget(null)
    }, [])

    // Switching between mode layers
    useEffect(() => {
        if (AppStore.mode.name === Mode.STOPS_AND_ROUTES.name) {
            mapController.focusOnLayer(mapController.stopsAndRoutesLayer)
        } else if (AppStore.mode.name === Mode.TRAFFIC_FLOW.name) {
            mapController.focusOnLayer(mapController.trafficFlowLayer)
        } else {
            mapController.focusOnLayer(mapController.stopsClusteringLayer)
        }
    }, [AppStore.mode])

    // Stops and routes data render
    useEffect(() => {
        mapController.stopsAndRoutesLayer.getSource().clear()
        if (AppStore.displayInfo.type === DisplayInfo.STOPS.type) {
            mapController.renderStops(AppStore.stopsAndRoutesData.stops)
        } else {
            mapController.renderRoutes(AppStore.stopsAndRoutesData.routes)
        }
        
    }, [AppStore.stopsAndRoutesData, AppStore.displayInfo])

    // Traffic flow data render
    useEffect(() => {
        mapController.trafficFlowLayer.getSource().clear()
        mapController.renderTraffic(AppStore.trafficFlowData.routes, AppStore.trafficFlowData.flow)
        
    }, [AppStore.trafficFlowData])

    // Stops clustering data render
    useEffect(() => {
        mapController.stopsClusteringLayer.getSource().clear()
        if (AppStore.stopsClusteringData.clusteredReferenceStops.length === 0) {
            mapController.renderReferenceStops(AppStore.stopsClusteringData.referenceStops)
        } else {
            StopsClusteringStyles.generateStyles(AppStore.stopsClusteringData.clustersCount)
            mapController.renderClusteredReferenceStops(AppStore.stopsClusteringData.clusteredReferenceStops)
        }
    }, [AppStore.stopsClusteringData])

    useEffect(() => {
        if (AppStore.highlightedMapEntity) {
            mapController.highlightMapEntity(AppStore.highlightedMapEntity)
        } else if (!AppStore.selectedMapEntity) {
            if (AppStore.showAll) {
                mapController.showAllFeatures()
            } else {
                mapController.hideAllFeatures()
            }
        }
            
    }, [AppStore.highlightedMapEntity])

    useEffect(() => {
        if (AppStore.selectedMapEntity)
            mapController.focusOnMapEntity(AppStore.selectedMapEntity)
        else if (AppStore.showAll)
            mapController.showAllFeatures()
    }, [AppStore.selectedMapEntity])

    useEffect(() => {
        if (AppStore.showAll) {
            mapController.showAllFeatures()
        } else {
            mapController.hideAllFeatures()
        }
    }, [AppStore.showAll])
    

    // Editing BBox
    useEffect(() => {
        if (isEditingBBox) {

            // Creating Map callback for drawing new bbox
            const draw = new Draw({source: mapController.bboxLayer.getSource(), type: 'Circle', geometryFunction: createBox()})
            draw.on('drawend', (e) => {
                mapController.bboxLayer.getSource().clear()
                AppStore.setBBox(e.feature.getGeometry().getExtent())
                setIsEditingBBox(false)
            })

            // Adding drawing callback
            mapController.map.addInteraction(draw)
        } else {
            // Remove drawing callback
            mapController.map.getInteractions().pop()
        }
    }, [isEditingBBox])

    useEffect(() => {
        if (AppStore.fetchInfo)
            fetchInfoRef.current.innerHTML = AppStore.fetchInfo
    }, [AppStore.fetchInfo])

    useEffect(() => {
        console.log(toJS(AppStore.stopsAndRoutesData))
    }, [AppStore.stopsAndRoutesData])

    const fetchInfoRef = useRef(null)

    return (
        <div className='MapContainer'>

            <div className='MapOverlay'>
                <RequestDataForm/>
            </div>
            
            <div className='Map' ref={mapElementRef} />

            <div className='MapTools'>

                <button className={isEditingBBox ? "Selected" : null} onClick={() => setIsEditingBBox(prev => !prev)}>
                    Рабочая область
                </button>
                
                <button onClick={() => {
                    mapController.allLayers.forEach(fl => fl.getSource().clear())
                    AppStore.clearBBox()
                    AppStore.clearStopsAndRoutesData()
                    AppStore.clearTrafficFlowData()
                    AppStore.clearClusteringData()
                }}>
                    Очистить карту
                </button>

                <button onClick={() => AppStore.toggleShowAll()}>
                    По умолчанию: {AppStore.showAll ? "Показывать" : "Скрывать"}
                </button>
            </div>
            
            <div ref={popupRef} className={"MapPopup"} />

            {AppStore.fetchInfo 
                ? <div ref={fetchInfoRef} onClick={() => AppStore.clearFetchInfo()} className={"FetchInfo " + AppStore.fetchStatus}/>
                : null
            }
            
        </div>
    )
})

export default MapContainer