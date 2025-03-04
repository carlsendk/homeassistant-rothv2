"""Mock for pytouchline_extended library."""


class MockRoom:
    """Mock representation of a Room."""

    def __init__(self, name, id, state, setpoint, sensor_temp, actual_setpoint, mode):
        """Initialize the mock room."""
        self.name = name
        self.id = id
        self.state = state
        self.setpoint = setpoint
        self.sensor_temp = sensor_temp
        self.actual_setpoint = actual_setpoint
        self.mode = mode


class MockTouchlineConnection:
    """Mock representation of the TouchlineConnection."""

    def __init__(self, host="192.168.1.100"):
        """Initialize the mock connection."""
        self.host = host
        self.connected = False
        self.rooms = [
            MockRoom(
                name="Living Room",
                id=1,
                state="Heat",
                setpoint=21.0,
                sensor_temp=20.5,
                actual_setpoint=21.0,
                mode="Normal",
            ),
            MockRoom(
                name="Bedroom",
                id=2,
                state="Off",
                setpoint=20.0,
                sensor_temp=19.5,
                actual_setpoint=20.0,
                mode="Night",
            ),
        ]

    async def connect(self):
        """Mock connect method."""
        if self.host == "invalid_host":
            raise ValueError("Cannot connect")
        self.connected = True
        return True

    async def disconnect(self):
        """Mock disconnect method."""
        self.connected = False
        return True

    async def get_rooms(self):
        """Mock get_rooms method."""
        return self.rooms

    async def set_setpoint(self, room_id, temperature):
        """Mock set_setpoint method."""
        for room in self.rooms:
            if room.id == room_id:
                room.setpoint = temperature
                room.actual_setpoint = temperature
                return True
        return False

    async def set_mode(self, room_id, mode):
        """Mock set_mode method."""
        valid_modes = ["Normal", "Night", "Holiday", "Program1", "Program2", "Program3"]
        if mode not in valid_modes:
            return False

        for room in self.rooms:
            if room.id == room_id:
                room.mode = mode
                return True
        return False

    async def set_state(self, room_id, state):
        """Mock set_state method."""
        valid_states = ["Heat", "Off"]
        if state not in valid_states:
            return False

        for room in self.rooms:
            if room.id == room_id:
                room.state = state
                return True
        return False

    async def refresh_devices(self):
        """Mock refresh_devices method."""
        return True
