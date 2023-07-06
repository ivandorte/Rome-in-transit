# Roma mobilità - GTFS-RT vehicle positions feed
CORS_GTFS_VEHICLE_POS = "https://corsproxy.io/?https://romamobilita.it/sites/default/files/rome_rtgtfs_vehicle_positions_feed.pb"

# Roma mobilità - GTFS-RT trip_updates
CORS_GTFS_TRIP_UPDATES = "https://corsproxy.io/?https://romamobilita.it/sites/default/files/rome_rtgtfs_trip_updates_feed.pb"

# Administrative boundaries of Rome - ISTAT (2022)
ADMIN_BOUNDS = "https://raw.githubusercontent.com/ivandorte/Rome-in-transit/main/data/RomeAdmin.geojson"

# Dashboard description
DASH_DESC = f"""
    <div>
        <hr />
        <p>
            This dashboard displays the near real-time position of any bus, tram,
            or train (ATAC and Roma TPL operators) within the Metropolitan
            City of Rome Capital.
        </p>
        <p>
            The <b>stream layers</b> automatically updates every 10 seconds
            with new data retrieved from the <a href="https://developers.google.com/transit/gtfs-realtime" target="_blank">GTFS-RealTime feed</a>
            provided and mantained by <a href="https://romamobilita.it/it/tecnologie" target="_blank">Roma Mobilità</a>.
        </p>
        <p>
            <a href="https://www.istat.it/it/archivio/222527" target="_blank">Administrative boundary (2022)</a> from ISTAT.
        </p>
        <hr />
    </div>
    """
