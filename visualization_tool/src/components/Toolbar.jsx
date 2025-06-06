import './Toolbar.css'
import AppStore, { DisplayInfo, Mode, Source } from "../store/AppStore";
import { observer } from "mobx-react-lite";
import { fetchBusData } from '../api/APIHandler';

const Toolbar = observer(() => {

    const { setMode, setSource } = AppStore;

    return <div className="Toolbar">
        <button 
            className={AppStore.mode.name === Mode.STOPS_AND_ROUTES.name ? 'Selected' : null} 
            onClick={() => {
                setMode(Mode.STOPS_AND_ROUTES)
                setSource(Source.LOCAL)
            }
        }>Остановки и маршруты</button>
        <button 
            className={AppStore.mode.name === Mode.TRAFFIC_FLOW.name ? 'Selected' : null}
            onClick={() => {
                setMode(Mode.TRAFFIC_FLOW)
                setSource(Source.TOMTOM)
                if (AppStore.bbox) {
                    AppStore.setFetchStatus("Loading")
                    AppStore.setFetchInfo("Получение данных о загруженности дорог...")
                    fetchBusData(AppStore.bbox, Source.LOCAL)
                        .then(res => AppStore.setTrafficRoutes(res.routes))
                        .then(() => AppStore.clearFetchInfo())
                } 
            }
        }>Загруженность дорог</button>
        <button
            className={AppStore.mode.name === Mode.STOPS_CLUSTERING.name ? 'Selected' : null}
            onClick={() => {
                setMode(Mode.STOPS_CLUSTERING)
                setSource(Source.DATA_MOS)
            }
        }>Кластеризация остановок</button>
    </div>

});

export default Toolbar