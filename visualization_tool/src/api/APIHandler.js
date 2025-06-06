import { toJS } from "mobx";

const API_URL = import.meta.env.VITE_API_BASE_URL;

// Fetch bus data (stops, obstacles and routes) from API
export const fetchBusData = async (bbox, source) => {
    const endpoint = `${API_URL}/bus_data/?source=${source.apiCode}&bbox=${bbox[0]}&bbox=${bbox[1]}&bbox=${bbox[2]}&bbox=${bbox[3]}`
    const response = await fetch(endpoint)
    return await response.json()
}

export const fetchCreateStops = async (stops) => {
    const endpoint = `${API_URL}/bus_data/stops`
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(stops)
    })

    return await response.json()
}

export const fetchDeleteStop = async (stopId) => {
    const endpoint = `${API_URL}/bus_data/stops`
    await fetch(endpoint, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify([stopId])
    })
}

export const fetchCreateRoute = async (route) => {

    const endpoint = `${API_URL}/bus_data/routes`
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify([route])
    })
    return await response.json()
}

export const fetchDeleteRoute = async (routeId) => {
    const endpoint = `${API_URL}/bus_data/routes`
    await fetch(endpoint, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify([routeId])
    })
}

export const fetchGetLocalRoutes = async (routesIds) => {
    const endpoint = `${API_URL}/bus_data/routes_by_id`
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(routesIds)
    })

    return await response.json()
}

export const fetchGetLocalRoutesInBBox = async (bbox) => {
    const endpoint = `${API_URL}/bus_data/routes?source=local&bbox=${bbox[0]}&bbox=${bbox[1]}&bbox=${bbox[2]}&bbox=${bbox[3]}`
    const response = await fetch(endpoint)
    return await response.json()
} 

export const fetchGetLocalStops = async (bbox) => {
    const endpoint = `${API_URL}/bus_data/stops?source=local&bbox=${bbox[0]}&bbox=${bbox[1]}&bbox=${bbox[2]}&bbox=${bbox[3]}`
    const response = await fetch(endpoint)
    return await response.json()
}



export const fetchSpeedDataList = async () => {
    const endpoint = `${API_URL}/traffic_flow/data/list`
    const response = await fetch(endpoint)
    return await response.json()
}

export const fetchLoadSpeedData = async (name, files) => {
    const endpoint = `${API_URL}/traffic_flow/data`
    const formData = new FormData()
    formData.append('speed_data_files', files[0])
    formData.append('speed_data_files', files[1])
    formData.append('speed_data_files', files[2])
    formData.append('speed_data_files', files[3])
    formData.append('speed_data_files', files[4])
    formData.append('speed_data_files', files[5])
    formData.append('speed_data_files', files[6])
    formData.append('name', name)

    const response = await fetch(endpoint, {
        method: 'POST',
        body: formData
    })

    return await response.json()
}

export const fetchCreateSpeedProfile = async (name, speedDataId, routesIds) => {
    const endpoint = `${API_URL}/traffic_flow`
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            routes_ids: routesIds,
            speed_data_id: speedDataId
        })
    })

    return await response.json()
}

export const fetchSpeedProfileList = async () => {
    const endpoint = `${API_URL}/traffic_flow/list`
    const response = await fetch(endpoint)
    return await response.json()
}

export const fetchGetSpeedProfile = async (speedProfileId) => {
    const endpoint = `${API_URL}/traffic_flow/${speedProfileId}`
    const response = await fetch(endpoint)
    return await response.json()
}

export const fetchDeleteSpeedProfile = async (speedProfileId) => {
    const endpoint = `${API_URL}/traffic_flow/${speedProfileId}`
    const response = await fetch(endpoint, {
        method: 'DELETE'
    })
    return await response.json()
}



export const fetchGenerateClusteringProfile = async (name, clusteringDataId) => {
    const endpoint = `${API_URL}/stops_clustering/generate`
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            params: {
                algorithm: "hdbscan_knn",
                min_score: 0.7,
                clustering_data_id: clusteringDataId
            }
        })
    })
    return await response.json()
}

export const fetchRealizeClusteringProfile = async (templateProfile) => {
    const endpoint = `${API_URL}/stops_clustering/realize`
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(templateProfile)
    })
    return await response.json()
}

export const fetchClusteringProfileList = async () => {
    const endpoint = `${API_URL}/stops_clustering/list`
    const response = await fetch(endpoint)
    return await response.json()
}

export const fetchClusteringDataList = async () => {
    const endpoint = `${API_URL}/stops_clustering/data/list`
    const response = await fetch(endpoint)
    return await response.json()
}

export const fetchLoadClusteringData = async (name, file) => {
    const endpoint = `${API_URL}/stops_clustering/data`
    const formData = new FormData()
    formData.append('clustering_data_file', file)
    formData.append('name', name)

    const response = await fetch(endpoint, {
        method: 'POST',
        body: formData
    })

    return await response.json()
}

export const fetchApplyClusteringProfile = async (clusteringProfile, stops) => {
    const endpoint = `${API_URL}/stops_clustering/${clusteringProfile.id}`
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(stops.map(s => s.id))
    })
    return await response.json()
}

export const fetchDeleteClusteringProfile = async (clusteringProfileId) => {
    const endpoint = `${API_URL}/stops_clustering/${clusteringProfileId}`
    const response = await fetch(endpoint, {
        method: 'DELETE'
    })
    const res = await response.json()
    console.log(res)
    return res
}
