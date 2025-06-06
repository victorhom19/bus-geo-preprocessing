import './InfoPanel.css'
import { useEffect, useState } from 'react';
import { observer } from 'mobx-react-lite';
import AppStore, { DisplayInfo, Mode, Source } from '../store/AppStore';
import { capitalizeString, colorLerp } from '../../utils';
import { fetchCreateRoute, fetchCreateStops, fetchDeleteRoute, fetchDeleteStop } from '../api/APIHandler';
import { toJS } from 'mobx';
import { LineString } from 'ol/geom';
import { getLength } from 'ol/sphere'
import { Projection } from 'ol/proj';


const StopInfo = observer(() => {

    const stop = AppStore.selectedMapEntity

    return (
        <>
            <div>Источник: {stop.source}</div>
            <div>Идентификатор: {stop.id}</div>
            <div>Название: {stop.name}</div>
            <div>Координаты: {stop.lon}, {stop.lat} </div>
            <div>Статус синхронизации: {stop.source === Source.LOCAL.apiCode ? "Синхронизировано" : "Не синхронизировано"}</div>
            <div className="Controls">
                <button className="Back" onClick={() => AppStore.clearSelectedMapEntity()}>Назад</button>
                {
                    AppStore.selectedMapEntity.source !== Source.LOCAL.apiCode
                    ? <button className="Sync" onClick={() => 
                        fetchCreateStops([AppStore.selectedMapEntity]).then(res => {
                            const updatedMapEntity = {...AppStore.selectedMapEntity, id: res[0].id, source: res[0].source}
                            AppStore.setStopsAndRoutesData({
                                ...AppStore.stopsAndRoutesData, 
                                stops: AppStore.stopsAndRoutesData.stops.map(s => s.id === AppStore.selectedMapEntity.id ? updatedMapEntity : s)
                            })
                            AppStore.setSelectedMapEntity(updatedMapEntity)
                        }
                    )}>
                        Синхронизировать остановку
                    </button>
                    : <button className="Delete" onClick={() => {
                        fetchDeleteStop(AppStore.selectedMapEntity.id)
                        AppStore.setStopsAndRoutesData({
                            ...AppStore.stopsAndRoutesData, 
                            stops: AppStore.stopsAndRoutesData.stops
                                        .map(s => s.id !== AppStore.selectedMapEntity.id ? s : {
                                            ...s, 
                                            id: 
                                            s.external_source_id, 
                                            source: Source.OSM.apiCode
                            })
                        })
                        AppStore.clearSelectedMapEntity()
                    }}>
                        Удалить остановку
                    </button>
                }
            </div>
            
        </>
    )

})

const RouteInfo = observer(() => {

    const route = AppStore.selectedMapEntity

    const renderSyncButtonSwitch = () => {
        return (
            AppStore.selectedMapEntity.source !== Source.LOCAL.apiCode ?
            (
                <button className="Sync" onClick={() => {

                    fetchCreateRoute(AppStore.selectedMapEntity).then(res => {
                        AppStore.setStopsAndRoutesData({
                            ...AppStore.stopsAndRoutesData, 
                            routes: AppStore.stopsAndRoutesData.routes.map(r => r.id === AppStore.selectedMapEntity.id ? res[0] : r)
                        })
                        AppStore.setSelectedMapEntity(AppStore.stopsAndRoutesData.routes.find(r => r.id === res[0].id))
                    })
                    
                }}>
                    Синхронизировать маршрут
                </button>
            ) : <button className="Delete" onClick={() => {
                    fetchDeleteRoute(AppStore.selectedMapEntity.id)
                    AppStore.setStopsAndRoutesData({
                        ...AppStore.stopsAndRoutesData, 
                        routes: AppStore.stopsAndRoutesData.routes
                                    .map(r => r.id !== AppStore.selectedMapEntity.id 
                                            ? r 
                                            : {
                                                ...r, 
                                                id: r.external_source_id, 
                                                source: Source.OSM.apiCode
                                            }
                                    )
                    })
                    AppStore.clearSelectedMapEntity()
                }}>
                    Удалить маршрут
                </button>
        )
    }

    return (
        <>
            <div>Источник: {route.source}</div>
            <div>Идентификатор: {route.id}</div>
            <div>Название: {route.name}</div>
            <div>Статус синхронизации: {route.source === Source.LOCAL.apiCode ? "Синхронизировано" : "Не синхронизировано"}</div>
            <div style={{display: 'flex', flexDirection: 'column'}}>
                {route.stops.map((stop, i) => 
                    <>
                        { i < route.stops.length - 1 && i !== route.final_stop_order
                            ? <> {
                                i <= route.final_stop_order 
                                    ? <>
                                        <div className="Entry" key={i}>
                                            {i+1}. {capitalizeString(stop.name)}
                                        </div>
                                        <div className="Entry" key={2 * i}>
                                            {Number(route.segments[i].distance).toFixed(2)}
                                        </div>
                                    </>
                                    : <>
                                        <div className="Entry" key={i}>
                                            {i}. {capitalizeString(stop.name)}
                                        </div>
                                        <div className="Entry" key={2 * i}>
                                            {Number(route.segments[i-1].distance).toFixed(2)}
                                        </div>
                                    </>
                            }</>
                            : null
                        }
                    </>
                )}
                <div className="Entry">
                    {route.stops.length-1}. {capitalizeString(route.stops[route.stops.length-1].name)}
                </div>
            </div>
            <div className="Controls">
                <button className="Back" onClick={() => AppStore.clearSelectedMapEntity()}>Назад</button>
                {renderSyncButtonSwitch()}
            </div>
        </>
    )

})


const StopsAndRoutesInfo = observer(() => {

    const [searchQuery, setSearchQuery] = useState('')

    const renderMapEntityInfoSwitch = () => {
        switch (AppStore.displayInfo.name) {
            case DisplayInfo.STOPS.name:
                return <StopInfo/>
            case DisplayInfo.ROUTES.name:
                return <RouteInfo/>
        }
    }

    const renderMapEntitiesListSwitch = () => {
        switch (AppStore.displayInfo.name) {
            case DisplayInfo.STOPS.name:
                return AppStore.stopsAndRoutesData.stops
                            .filter(stop => stop.name.toLowerCase().includes(searchQuery.toLowerCase()))
                            .sort((a, b) => a.name.localeCompare(b.name))
                            .map((stop, i) => <div 
                                key={i} 
                                onMouseEnter={() => AppStore.setHighlightedMapEntity(stop)} 
                                onClick={() => AppStore.setSelectedMapEntity(stop)}>
                                    {i+1}. {capitalizeString(stop.name)}
                                </div>
                            )
            case DisplayInfo.ROUTES.name:
                return AppStore.stopsAndRoutesData.routes
                            .filter(route => route.name.toLowerCase().includes(searchQuery.toLowerCase()))
                            .sort((a, b) => a.name.localeCompare(b.name))
                            .map((route, i) => <div 
                                key={i} 
                                onMouseEnter={() => AppStore.setHighlightedMapEntity(route)} 
                                onClick={() => AppStore.setSelectedMapEntity(route)}>
                                    {i+1}. {capitalizeString(route.name)}
                                </div>
                            )
        }
    }

    return <>
        <div className='Header'>
            <button
                className={AppStore.displayInfo.name === DisplayInfo.STOPS.name ? 'Selected' : null}
                onClick={() => {
                    AppStore.setDisplayInfo(DisplayInfo.STOPS)
                    AppStore.clearSelectedMapEntity()
                }}
            >Остановки</button>
            <button 
                className={AppStore.displayInfo.name === DisplayInfo.ROUTES.name ? 'Selected' : null}
                onClick={() => {
                    AppStore.setDisplayInfo(DisplayInfo.ROUTES)
                    AppStore.clearSelectedMapEntity()
                }}
            >Маршруты</button>
        </div>
        {!AppStore.selectedMapEntity 
            ? <div className='Search'>
                <input value={searchQuery} placeholder='Поиск...' onChange={e => setSearchQuery(e.target.value)}/>
            </div>
            : null
        }
        <div className='Content' onMouseLeave={() => AppStore.setHighlightedMapEntity(null)}>
            {AppStore.selectedMapEntity ? renderMapEntityInfoSwitch() : renderMapEntitiesListSwitch()}
        </div>
    </>
})

const RouteTrafficInfo = observer(() => {

    const route = AppStore.selectedMapEntity
    const routeTrafficFlow = AppStore.trafficFlowData.flow[route.id]

    const getColor = (speed) => {
        let color = 'rgb(118, 118, 118)'
        if (speed) {
            const ratio = Math.min(1.0, speed / 60)
            if (ratio < 0.5) {
                color = colorLerp("#aa0000", "#aaaa00", 2 * ratio)
            } else {
                color = colorLerp("#aaaa00", "#00aa00", 2 * (ratio - 0.5))
            }
        }
        return color
    }

    const generateLabel = (i) => {
        const trafficFlowSegment = routeTrafficFlow[i]
        const routeSegment = route.segments[i]
        let obstaclesCount = routeSegment.crossings + routeSegment.traffic_signals + 
                                routeSegment.speedbumps + routeSegment.roundabouts
        if (obstaclesCount >= 20) {
            obstaclesCount = obstaclesCount % 10
        }

        if (obstaclesCount === 0) {
            return `${Number(trafficFlowSegment).toFixed(2)} км/ч`
        } else if (5 <= obstaclesCount && obstaclesCount <= 20 || obstaclesCount % 10 === 0) {
            return `${Number(trafficFlowSegment).toFixed(2)} км/ч + ${obstaclesCount} препятствий`
        } else if (obstaclesCount % 10 === 1) {
            return `${Number(trafficFlowSegment).toFixed(2)} км/ч + ${obstaclesCount} препятствие`
        } else if (2 <= obstaclesCount % 10 && obstaclesCount % 10 <= 4) {
            return `${Number(trafficFlowSegment).toFixed(2)} км/ч + ${obstaclesCount} препятствия`
        }
    }

    return (
        <>
            <div>Источник: {route.source}</div>
            <div>Идентификатор: {route.id}</div>
            <div>Название: {route.name}</div>
            <div style={{display: 'flex', flexDirection: 'column'}}>
                {route.stops.map((stop, i) => 
                    <>
                        { i < route.stops.length - 1 && i !== route.final_stop_order
                            ? <> {
                                i <= route.final_stop_order 
                                    ? <>
                                        <div className="Entry" key={2 * i}>
                                            {i+1}. {capitalizeString(stop.name)}
                                        </div>
                                        <div className="Entry" key={2 * i + 1} style={{borderColor: getColor(routeTrafficFlow[i])}}>
                                            {generateLabel(i)}
                                        </div>
                                    </>
                                    : <>
                                        <div className="Entry" key={2 * i}>
                                            {i}. {capitalizeString(stop.name)}
                                        </div>
                                        <div className="Entry" key={2 * i + 1} style={{borderColor: getColor(routeTrafficFlow[i-1])}}>
                                            {generateLabel(i-1)}
                                        </div>
                                    </>
                            }</>
                            : null
                        }
                    </>
                )}
            <div className="Entry">
                {route.stops.length-1}. {capitalizeString(route.stops[route.stops.length-1].name)}
            </div>
            </div>
            <div className="Controls">
                <button className="Back" onClick={() => AppStore.clearSelectedMapEntity()}>Назад</button>
            </div>
        </>
    )
})

const TrafficFlowInfo = observer(() => {

    const [searchQuery, setSearchQuery] = useState('')

    const renderMapEntitiesList = () => {
        return AppStore.trafficFlowData.routes
            .filter(route => route.name.toLowerCase().includes(searchQuery.toLowerCase()))
            .sort((a, b) => a.name.localeCompare(b.name))
            .map((route, i) => <div 
                key={route.id} 
                onMouseEnter={() => AppStore.setHighlightedMapEntity(route)} 
                onClick={() => AppStore.setSelectedMapEntity(route)}>
                    {i+1}. {capitalizeString(route.name)}
                </div>)
    }

    return <>
        <div className='Header'>
            <button className='Selected'>Загруженность дорог</button>
        </div>
        {!AppStore.selectedMapEntity 
            ? <div className='Search'>
                <input value={searchQuery} placeholder='Поиск...' onChange={e => setSearchQuery(e.target.value)}/>
            </div>
            : null
        }
        <div className='Content' onMouseLeave={() => AppStore.setHighlightedMapEntity(null)}>
            {AppStore.selectedMapEntity ? <RouteTrafficInfo/> : renderMapEntitiesList()}
        </div>
    </>
})

const StopsClusterringInfo = observer(() => {

    const [searchQuery, setSearchQuery] = useState('')

    const renderMapEntitiesList = () => {
        return AppStore.stopsClusteringData.clusteredReferenceStops
            .filter(stop => stop.name.toLowerCase().includes(searchQuery.toLowerCase()))
            .sort((a, b) => a.name.localeCompare(b.name))
            .map((route, i) => <div 
                key={route.id} 
                onMouseEnter={() => AppStore.setHighlightedMapEntity(route)} 
                onClick={() => AppStore.setSelectedMapEntity(route)}>
                    {i+1}. {capitalizeString(route.name)}
                </div>)
    }

    return <>
        <div className='Header'>
            <button className='Selected'>Кластеризация остановок</button>
        </div>
        {!AppStore.selectedMapEntity 
            ? <div className='Search'>
                <input value={searchQuery} placeholder='Поиск...' onChange={e => setSearchQuery(e.target.value)}/>
            </div>
            : null
        }
        <div className='Content' onMouseLeave={() => AppStore.setHighlightedMapEntity(null)}>
            {renderMapEntitiesList()}
        </div>
    </>
})

const InfoPanel = observer(() => {

    const renderMode = () => {
        switch (AppStore.mode.name) {
            case Mode.STOPS_AND_ROUTES.name:
                return <StopsAndRoutesInfo/>
            case Mode.TRAFFIC_FLOW.name:
                return <TrafficFlowInfo/>
            case Mode.STOPS_CLUSTERING.name:
                return <StopsClusterringInfo/>
        }
    }

    return <div className="InfoPanel">
        {renderMode()}
    </div>
})

export default InfoPanel