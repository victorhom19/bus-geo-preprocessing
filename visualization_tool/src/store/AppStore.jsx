import { makeAutoObservable } from "mobx";


// ----- Defining Enums -----

export const Mode = Object.freeze({
    STOPS_AND_ROUTES: { name: "STOPS_AND_ROUTES" },
    TRAFFIC_FLOW: { name: "TRAFFIC_FLOW" },
    STOPS_CLUSTERING: { name: "STOPS_CLUSTERING" }
})

export const Source = Object.freeze({
    LOCAL: { name: "LOCAL", apiCode: "local" },
    OSM: { name: "OSM", apiCode: "osm" },
    TOMTOM: { name: "TOMTOM", apiCode: "tomtom" },
    HERE: { name: "HERE", apiCode: "here" },
    DATA_MOS: { name: "DATA_MOS", apiCode: "data_mos" }
})

export const DisplayInfo = Object.freeze({
    STOPS: { name: "STOPS", type: 'stop' },
    ROUTES: { name: "ROUTES", type: 'route' }
})

class AppStore {

    // Make store observable
    constructor() { makeAutoObservable(this) }

    // Mode field
    mode = Mode.STOPS_AND_ROUTES
    setMode = (newMode) => {this.mode = newMode}

    // Display info field
    displayInfo = DisplayInfo.STOPS
    setDisplayInfo = (newDisplayInfo) => {this.displayInfo = newDisplayInfo}

    // BBox field
    bbox = null
    setBBox = (newBBox) => {this.bbox = newBBox}
    clearBBox = () => {this.bbox = null}

    // Source field
    source = Source.LOCAL
    setSource = (newSource) => {this.source = newSource}
    
    // // Data field
    // data = {stops: [], obstacles: [], routes: []}
    // setData = (newData) => {this.data = newData}
    // clearData = () => {}

    // Stops and routes data
    stopsAndRoutesData = {stops: [], routes: []}
    setStopsAndRoutesData = (newData) => {this.stopsAndRoutesData = newData}
    clearStopsAndRoutesData = () => {this.stopsAndRoutesData = {stops: [], routes: []}}

    // Traffic flow data
    trafficFlowData = {routes: [], flow: {}, weekday: 'monday', hourInterval: 0}
    setTrafficRoutes = (routes) => {this.trafficFlowData = {...this.trafficFlowData, routes: routes}}
    setTrafficFlow = (flow) => {this.trafficFlowData = {...this.trafficFlowData, flow: flow}}
    setTrafficTime = (weekday, hourInterval) => {this.trafficFlowData = {...this.trafficFlowData, weekday: weekday, hourInterval: hourInterval}}
    clearTrafficFlowData = () => {this.trafficFlowData = {routes: [], flow: {}, weekday: 'monday', hourInterval: 0}}

    // Stops clustering data
    stopsClusteringData = {referenceStops: [], clusteredReferenceStops: [], score: 0, clustersCount: 0}
    setReferenceStops = (referenceStops) => {this.stopsClusteringData = {...this.stopsClusteringData, referenceStops: referenceStops}}
    setClusteredReferenceStops = (clusteredReferenceStops) => {
        this.stopsClusteringData = {...this.stopsClusteringData, clusteredReferenceStops: clusteredReferenceStops}}
    setClustersCount = (clustersCount) => {this.stopsClusteringData = {...this.stopsClusteringData, clustersCount: clustersCount}}
    setScore = (score) => {this.stopsClusteringData = {...this.stopsClusteringData, score: score}}
    clearClusteringData = () => {this.stopsClusteringData = {referenceStops: [], clusteredReferenceStops: [], score: 0,
                                 clustersCount: 0}}

    // Focused map entity
    focusedMapEntity = null
    setFocusedMapEntity = (newMapEntity) => {this.focusedMapEntity = newMapEntity}
    clearFocusedMapEntity = () => {this.focusedMapEntity = null}

    // Selected map entity
    selectedMapEntity = null
    setSelectedMapEntity = (newMapEntity) => {this.selectedMapEntity = newMapEntity}
    clearSelectedMapEntity = () => {this.selectedMapEntity = null}

    // Show all features
    showAll = true
    toggleShowAll = () => {this.showAll = !this.showAll}

    highlightedMapEntity = null
    setHighlightedMapEntity = (newMapEntity) => {this.highlightedMapEntity = newMapEntity}
    clearHighlightedMapEnitty = () => {this.highlightedMapEntity = null}
    
    fetchInfo = null
    setFetchInfo = (message) => {this.fetchInfo = message}
    clearFetchInfo = () => {this.fetchInfo = null}

    fetchStatus = null
    setFetchStatus = (newStatus) => {this.fetchStatus = newStatus}

}

export default new AppStore()