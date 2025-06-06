import { useEffect, useState } from 'react'
import './RequestDataForm.css'
import { observer } from 'mobx-react-lite'
import AppStore, { Mode, Source } from '../store/AppStore'
import { fetchApplyClusteringProfile, fetchBusData, fetchClusteringDataList, fetchClusteringProfileList, fetchCreateSpeedProfile, fetchDeleteClusteringProfile, fetchDeleteSpeedProfile, fetchGenerateClusteringProfile, fetchGetLocalRoutes, fetchGetLocalRoutesInBBox, fetchGetLocalStops, fetchGetSpeedProfile, fetchLoadClusteringData, fetchLoadSpeedData, fetchRealizeClusteringProfile, fetchSpeedDataList, fetchSpeedProfileList} from '../api/APIHandler'
import Select from 'react-select'
import { toJS } from 'mobx'


const StopsAndRoutesRequestForm = () => {

    const options = [Source.LOCAL, Source.OSM]
    const [source, setSource] = useState(Source.LOCAL)

    return <div className='Content'>
        <div className='Entry'>
            <div className='Label'>Источник данных:</div>
            <select onChange={e => setSource(options[e.target.value])}>
                {options.map((opt, i) => <option key={opt.name} value={i}>{opt.name}</option>)}
            </select>
        </div>
        <button className='Submit' onClick={() => {
            if (!AppStore.bbox) {
                AppStore.setFetchStatus("Error")
                AppStore.setFetchInfo("Не определена рабочая область!")
            } else {
                AppStore.setFetchStatus("Loading")
                AppStore.setFetchInfo("Получение данных об остановках и маршрутах...")
                fetchBusData(AppStore.bbox, source)
                    .then(res => AppStore.setStopsAndRoutesData(res))
                    .then(() => AppStore.clearFetchInfo())
            }
            
        }}>Получить данные</button>
    </div>
}


const SpeedProfileInfo = ({backCallback, speedProfileId, updateSpeedProfileList}) => {
    
    const [weekday, setWeekday] = useState('monday')
    const [hourInterval, setHourInterval] = useState(0)

    const [routes, setRoutes] = useState([])
    const [speedProfile, setSpeedProfile] = useState(null)

    useEffect(() => {
        fetchGetSpeedProfile(speedProfileId).then(speedProfile => {
            setSpeedProfile(speedProfile)
            const routesIds = Object.keys(speedProfile.routes)
            fetchGetLocalRoutes(routesIds).then(routes => {
                setRoutes(routes)
            })
        })
    }, [])

    useEffect(() => {
        if (speedProfile !== null) {
            AppStore.setTrafficRoutes(routes)
            const trafficFlow = {}
            Object.keys(speedProfile.routes).forEach(key => {
                trafficFlow[key] = speedProfile.routes[key][weekday][hourInterval]
            })
            AppStore.setTrafficFlow(trafficFlow)
        }

    }, [speedProfile, weekday, hourInterval])

    const formatHourInterval = (h) => {
        const first = h < 10 ? '0' + h : h
        const second = (h+1)%24 < 10 ? '0' + (h+1)%24 : (h+1)%24
        return `${first}:00-${second}:00`
    }

    return <>
        {
            speedProfile ? 
            <>
                <div className='Entry'>
                    <div className='Label'>Профиль скорости: {speedProfile.name}</div>
                </div>
                <div className='Entry'>
                    <div className='Label'>День недели:</div>
                    <select onChange={e => {setWeekday(e.target.value); AppStore.setTrafficTime(weekday, hourInterval)}}>
                        <option value={'monday'}>Понедельник</option>
                        <option value={'tuesday'}>Вторник</option>
                        <option value={'wednesday'}>Среда</option>
                        <option value={'thursday'}>Четверг</option>
                        <option value={'friday'}>Пятница</option>
                        <option value={'saturday'}>Суббота</option>
                        <option value={'sunday'}>Воскресенье</option>
                    </select>
                </div>
                <div className='Entry'>
                    <div className='Label'>Временной интервал:</div>
                    <select onChange={e => {setHourInterval(Number(e.target.value)); AppStore.setTrafficTime(weekday, Number(e.target.value))}}>
                        {Array.from(Array(24).keys()).map(
                            h => <option key={h} value={h}>{formatHourInterval(h)}</option>
                        )}
                    </select>
                </div>
                <div className='Entry'>
                    <button className="Back" onClick={backCallback}>
                        Назад
                    </button>
                    <button className="Delete" onClick={() => {
                        AppStore.setFetchStatus("Loading")
                        AppStore.setFetchInfo("Удаление данных профиля...")
                        fetchDeleteSpeedProfile(speedProfile.id).then(res => {
                            updateSpeedProfileList(prev => prev.filter(profile => profile.id !== res.id))
                            backCallback()
                            AppStore.setFetchStatus("Result")
                            AppStore.setFetchInfo("Профиль удален!")
                        })
                    }}>
                        Удалить профиль
                    </button>
                </div>

            </>
            : <div className='Entry'>
                <div className='Label'>Загрузка данных профиля...</div>
            </div>
        }
    </>
}

const SpeedDataUploadWindow = ({backCallback, updateSpeedDataList}) => {

    const [name, setName] = useState("")
    const [mondayFile, setMondayFile] = useState([])
    const [tuesdayFile, setTuesdayFile] = useState([])
    const [wednesdayFile, setWednesdayFile] = useState([])
    const [thursdayFile, setThursdayFile] = useState([])
    const [fridayFile, setFridayFile] = useState([])
    const [saturdayFile, setSaturdayFile] = useState([])
    const [sundayFile, setSundayFile] = useState([])

    return <>
        <div className='Entry'>
            <div className='Label'>Название данных:</div>
            <input value={name} onChange={e => setName(e.target.value)}/>
        </div>
        <div className='Entry'>
            <div className='Label'>Данные скорости (понедельник):</div>
            <input type="file" id="input" onChange={e => setMondayFile(e.target.files[0])}/>
        </div>
        <div className='Entry'>
            <div className='Label'>Данные скорости (вторник):</div>
            <input type="file" id="input" onChange={e => setTuesdayFile(e.target.files[0])}/>
        </div>
        <div className='Entry'>
            <div className='Label'>Данные скорости (среда):</div>
            <input type="file" id="input" onChange={e => setWednesdayFile(e.target.files[0])}/>
        </div>
        <div className='Entry'>
            <div className='Label'>Данные скорости (четверг):</div>
            <input type="file" id="input" onChange={e => setThursdayFile(e.target.files[0])}/>
        </div>
        <div className='Entry'>
            <div className='Label'>Данные скорости (пятница):</div>
            <input type="file" id="input" onChange={e => setFridayFile(e.target.files[0])}/>
        </div>
        <div className='Entry'>
            <div className='Label'>Данные скорости (суббота):</div>
            <input type="file" id="input" onChange={e => setSaturdayFile(e.target.files[0])}/>
        </div>
        <div className='Entry'>
            <div className='Label'>Данные скорости (воскресенье):</div>
            <input type="file" id="input" onChange={e => setSundayFile(e.target.files[0])}/>
        </div>
        <div className='Entry'>
            <button className="Back" onClick={backCallback}>
                Назад
            </button>
            <button className="Submit" onClick={() => {
                AppStore.setFetchStatus("Loading")
                AppStore.setFetchInfo("Загрузка данных скорости...")
                fetchLoadSpeedData(
                    name, 
                    [mondayFile, tuesdayFile, wednesdayFile, thursdayFile, fridayFile, saturdayFile, sundayFile]
                ).then((res) => {
                    AppStore.setFetchStatus("Result")
                    AppStore.setFetchInfo("Данные скорости загружены!")
                    backCallback()
                    updateSpeedDataList(prev => [...prev, res])
                })
            }}>
                Загрузить данные скорости
            </button>
        </div>
        
    </>


}

const SpeedProfileCreateWindow = observer(({backCallback, updateSpeedProfileList}) => {
    const [name, setName] = useState("")
    const [selectedSpeedData, setSelectedSpeedData] = useState(null)

    const [speedDataList, setSpeedDataList] = useState([])

    const [isUploadingSpeedData, setIsUploadingSpeedData] = useState(false)

    const [routes, setRoutes] = useState([])

    useEffect(() => {
        if (AppStore.bbox)
            fetchGetLocalRoutesInBBox(AppStore.bbox).then(res => {
                setRoutes(res)
                AppStore.setTrafficRoutes(res)
    })
    }, [AppStore.bbox])

    useEffect(() => {
        if (!isUploadingSpeedData)
            fetchSpeedDataList().then(res => setSpeedDataList(res))
    }, [isUploadingSpeedData])

    return <>
        {
            !isUploadingSpeedData
                ? <>
                    <div className='Entry'>
                        <div className='Label'>Название профиля:</div>
                        <input value={name} onChange={e => setName(e.target.value)}/>
                    </div>
                    <div className='Entry'>
                        <div className='Label'>Исходные данные:</div>
                        <select
                            onChange={e => {
                                if (Number(e.target.value) === speedDataList.length) {
                                    setIsUploadingSpeedData(true)
                                } else {
                                    setSelectedSpeedData(speedDataList[e.target.value])
                                }
                            }}
                        >
                            <option disabled={true} selected={true} value={"Выберите данные"}> -- Выберите данные -- </option>
                            {

                                speedDataList.map((speedData, index) => 
                                    <option key={index} value={index}>{speedData.name}</option>
                                )
                            }
                            <option value={speedDataList.length}>Загрузить данные</option>
                        </select>
                    </div>
                    <div className='Entry'>
                        <div className='Label'>{`Выбрано маршрутов: ${routes.length}`}</div>
                    </div>
                    <div className='Entry'>
                        <button className="Back" onClick={backCallback}>
                            Назад
                        </button>
                        <button className="Submit" onClick={() => {
                            AppStore.setFetchStatus("Loading")
                            AppStore.setFetchInfo("Создание профиля скорости...")
                            fetchCreateSpeedProfile(
                                name, 
                                selectedSpeedData.id, 
                                AppStore.trafficFlowData.routes.map(r => r.id)
                            ).then(res => {
                                AppStore.setFetchStatus("Result")
                                AppStore.setFetchInfo("Профиль скорости создан!")
                                backCallback()
                                updateSpeedProfileList(prev => [...prev, res])
                            })
                        }}>
                            Создать профиль
                        </button>
                    </div>
                    
                </> : <SpeedDataUploadWindow 
                        backCallback={() => setIsUploadingSpeedData(false)}
                        updateSpeedDataList={setSpeedDataList}
                    />
        }
    </>
})


const TrafficFlowRequestForm = () => {

    const [selectedSpeedProfile, setSelectedSpeedProfile] = useState(null)
    const [isCreatingNewProfile, setIsCreatingNewProfile] = useState(false)

    const [speedProfileList, setSpeedProfileList] = useState([])

    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        setIsLoading(true)
        fetchSpeedProfileList().then(res => setSpeedProfileList(res)).then(() => setIsLoading(false))
    }, [])

    return <div className='Content'>
        {
            selectedSpeedProfile 
                ? <SpeedProfileInfo 
                    speedProfileId={selectedSpeedProfile.id} 
                    backCallback={() => setSelectedSpeedProfile(null)}
                    updateSpeedProfileList={setSpeedProfileList}
                />
                : isCreatingNewProfile
                    ? <SpeedProfileCreateWindow 
                        backCallback={() => setIsCreatingNewProfile(false)}
                        updateSpeedProfileList={setSpeedProfileList}
                    />
                    : <>
                        <div className='Entry'>
                            <div className='Label'>Профиль:</div>
                            {
                                isLoading
                                    ? <>Загрузка...</>
                                    : <select
                                            onChange={e => {
                                                if (Number(e.target.value) === speedProfileList.length) {
                                                    setIsCreatingNewProfile(true)
                                                } else {
                                                    setSelectedSpeedProfile(speedProfileList[e.target.value])
                                                }
                                            }}
                                        >
                                            <option disabled={true} selected={true} value={"Выберите профиль"}> -- Выберите профиль -- </option>
                                            {

                                                speedProfileList.map((speedProfile, index) => 
                                                    <option key={index} value={index}>{speedProfile.name}</option>
                                                )
                                            }
                                            <option value={speedProfileList.length}>Создать профиль</option>
                                        </select>
                            }
                        </div> 
                    </> 
        }
        
    </div>
}


const ClusteringDataUploadWindow = ({backCallback, updateClusteringDataList}) => {

    const [name, setName] = useState("")
    const [clusteringDataFile, setClusteringDataFile] = useState()

    return <>
        <div className='Entry'>
            <div className='Label'>Название данных:</div>
            <input value={name} onChange={e => setName(e.target.value)}/>
        </div>
        <div className='Entry'>
            <div className='Label'>Данные кластеризации:</div>
            <input type="file" id="input" onChange={e => setClusteringDataFile(e.target.files[0])}/>
        </div>
        <div className='Entry'>
            <button className="Back" onClick={backCallback}>
                Назад
            </button>
            <button className='Submit' onClick={() => {
                AppStore.setFetchStatus("Loading")
                AppStore.setFetchInfo("Загрузка данных кластеризации...")
                fetchLoadClusteringData(
                    name, 
                    clusteringDataFile
                ).then((res) => {
                    AppStore.setFetchStatus("Result")
                    AppStore.setFetchInfo("Данные кластеризации загружены!")
                    backCallback()
                    updateClusteringDataList(prev => [...prev, res])
                })
            }}>
                Загрузить данные кластеризации
            </button>
        </div>
        
    </>
}

const ClusterProfileCreateWindow = ({backCallback, updateClusteringProfileList}) => {

    const [name, setName] = useState("")

    const [selectedClusteringData, setSelectedClusteringData] = useState(null)

    const [clusteringDataList, setClusteringDataList] = useState([])

    const [isUploadingClusteringData, setIsUploadingClusteringData] = useState(false)

    const [clusteringTemplates, setClusteringTemplates] = useState([])

    useEffect(() => {
        fetchClusteringDataList().then(res => setClusteringDataList(res))
    }, [])

    return <>
        {
            !isUploadingClusteringData
                ? <>
                    {
                        clusteringTemplates.length === 0 
                        ? <>
                            <div className='Entry'>
                                <div className='Label'>Название профиля:</div>
                                <input value={name} onChange={e => setName(e.target.value)}/>
                            </div>
                            <div className='Entry'>
                                <div className='Label'>Данные кластеризации:</div>
                                <select
                                    onChange={e => {
                                        if (Number(e.target.value) === clusteringDataList.length) {
                                            setIsUploadingClusteringData(true)
                                        } else {
                                            setSelectedClusteringData(clusteringDataList[e.target.value])
                                        }
                                    }}
                                >
                                    <option disabled={true} selected={true} value={"Выберите данные"}> -- Выберите данные -- </option>
                                    {

                                        clusteringDataList.map((speedData, index) => 
                                            <option key={index} value={index}>{speedData.name}</option>
                                        )
                                    }
                                    <option value={clusteringDataList.length}>Загрузить данные</option>
                                </select>
                            </div>
                            <div className='Entry'>
                                <button className="Back" onClick={backCallback}>
                                    Назад
                                </button>
                                <button className='Submit' onClick={() => {
                                    AppStore.setFetchStatus("Loading")
                                    AppStore.setFetchInfo("Создание профиля кластеризации...")
                                    fetchGenerateClusteringProfile(
                                        name, 
                                        selectedClusteringData.id, 
                                    ).then(res => {
                                        AppStore.setFetchStatus("Result")
                                        AppStore.setFetchInfo("Созданы варианты профиля кластеризации!")
                                        setClusteringTemplates(res)
                                    })
                                }}>
                                    Сгенерировать профили
                                </button>
                            </div>
                            
                        </>
                        : <>
                            {
                                clusteringTemplates.map(template => 
                                    <div className='Entry' onClick={() => {
                                        AppStore.setFetchStatus("Loading")
                                        AppStore.setFetchInfo("Cоздание профиля кластеризации...")
                                        fetchRealizeClusteringProfile(template).then(res => {
                                            AppStore.setFetchStatus("Result")
                                            AppStore.setFetchInfo("Профиль кластеризации создан!")
                                            backCallback()
                                            updateClusteringProfileList(prev => [...prev, res])
                                        })
                                        
                                    }}>
                                        <div className='Label'>Полнота: {template.clustering_score.toFixed(2)}, количество кластеров: {template.clusters_count}</div>
                                    </div>
                                )
                            }
                        </>
                    }
                </> : <ClusteringDataUploadWindow 
                        backCallback={() => setIsUploadingClusteringData(false)}
                        updateClusteringDataList={setClusteringDataList}
                    />
        }
    </>
}

const ClusteringProfileInfo = observer(({clusteringProfile, backCallback, updateClusteringProfileList}) => {

    const [stops, setStops] = useState([])

    useEffect(() => {
        fetchGetLocalStops(AppStore.bbox).then(res => {
            setStops(res)
            AppStore.setReferenceStops(res)
    })
    }, [AppStore.bbox])

    return <>
        <div className='Entry'>
            <div className='Label'>Профиль кластеризации: {clusteringProfile.name}</div>
        </div>
        <div className='Entry'>
            <div className='Label'>Выбрано остановок: {stops.length}</div>
        </div>
        <div className='Entry'>
            <button className="Back" onClick={backCallback}>
                Назад
            </button>
            <button className="Delete" onClick={() => {
                AppStore.setFetchStatus("Loading")
                AppStore.setFetchInfo("Удаление данных профиля...")
                fetchDeleteClusteringProfile(clusteringProfile.id).then(res => {
                    updateClusteringProfileList(prev => prev.filter(profile => profile.id !== res.id))
                    backCallback()
                    AppStore.setFetchStatus("Result")
                    AppStore.setFetchInfo("Профиль удален!")
                })
            }}>
                Удалить профиль
            </button>
            <button className="Submit" onClick={() => {
                AppStore.setFetchStatus("Loading")
                AppStore.setFetchInfo("Кластеризация остановок")
                AppStore.setClustersCount(clusteringProfile.clusters_count)
                fetchApplyClusteringProfile(clusteringProfile, stops).then(res => {
                    AppStore.setClusteredReferenceStops(res.clustered_stops)
                    AppStore.setFetchStatus("Result")
                    AppStore.setFetchInfo("Остановки кластеризованы!")
                })
            }}>
                Применить профиль
            </button>

        </div>
        
    </>
})

const StopsClusteringRequestForm = () => {

    const [selectedClusteringProfile, setSelectedClusteringProfile] = useState(null)
    const [isCreatingNewProfile, setIsCreatingNewProfile] = useState(false)

    const [clusteringProfileList, setClusteringProfileList] = useState([])

    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        setIsLoading(true)
        fetchClusteringProfileList().then(res => setClusteringProfileList(res)).then(() => setIsLoading(false))
    }, [])

    return <div className='Content'>
        {
            selectedClusteringProfile 
                ? <ClusteringProfileInfo 
                    clusteringProfile={selectedClusteringProfile}
                    backCallback={() => setSelectedClusteringProfile(null)}
                    updateClusteringProfileList={setClusteringProfileList}
                />
                : isCreatingNewProfile
                    ? <ClusterProfileCreateWindow 
                        backCallback={() => setIsCreatingNewProfile(false)}
                        updateClusteringProfileList={setClusteringProfileList}
                    />
                    : <>
                        <div className='Entry'>
                            <div className='Label'>Профиль:</div>
                            {
                                isLoading
                                    ? <>Загрузка...</>
                                    : <select
                                        onChange={e => {
                                            if (Number(e.target.value) === clusteringProfileList.length) {
                                                setIsCreatingNewProfile(true)
                                            } else {
                                                setSelectedClusteringProfile(clusteringProfileList[e.target.value])
                                            }
                                        }}
                                    >
                                        <option disabled={true} selected={true} value={"Выберите профиль"}> -- Выберите профиль -- </option>
                                        {

                                            clusteringProfileList.map((clusteringProfile, index) => 
                                                <option key={index} value={index}>{clusteringProfile.name}</option>
                                            )
                                        }
                                        <option value={clusteringProfileList.length}>Создать профиль</option>
                                    </select>
                            }
                        </div> 
                    </> 
        }
    </div>
}

const RequestDataForm = observer(() => {
    
    const [expanded, setExpanded] = useState(false)

    const renderForm = () => {
        switch (AppStore.mode.name) {
            case Mode.STOPS_AND_ROUTES.name:
                return <StopsAndRoutesRequestForm/>
            case Mode.TRAFFIC_FLOW.name:
                return <TrafficFlowRequestForm/>
            case Mode.STOPS_CLUSTERING.name:
                return <StopsClusteringRequestForm/>
        }
    }

    return <div className='RequestDataForm'>
        {expanded 
            ? <button className={expanded ? 'Expanded' : null} onClick={() => setExpanded(false)}>Свернуть</button> 
            : <button className={expanded ? 'Expanded' : null} onClick={() => setExpanded(true)}>Данные</button>}
        {expanded ? renderForm() : null}
    </div>
})

export default RequestDataForm