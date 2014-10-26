'use strict'

angular.module('daemon.radio', [])

.service('radio', [
  '$interval'
  ($interval) ->
    radio = {}
    # whether or not we've initialized
    _init = false

    radio.initialized = ->
      return _init

    # thing
    _ndl3Radio = undefined

    # initialize typpo

    RADIO_PROTOCOL_YAML_FILE = "./radio_protocol_ng.yaml"
    typpo_module = requireNode('ndl3radio/factory')
    buffer = requireNode('buffer')

    typpo = typpo_module.make()
    typpo.set_target_type('ARM')
    typpo.load_type_file(RADIO_PROTOCOL_YAML_FILE, false)

    # an object of arrays, where the keys are
    # the channel of events to repond to
    # and the values are arrays of callbacks
    callbacks = {}

    # send an update to each callback that has registered with us
    # but only if the radio is initialized
    processUpdate = (channel, update) ->
      if _init and callbacks[channel]?
        callback(channel, update) for callback in callbacks[channel]

    # fake radio event sent every 100 ms
    mock = false
    mockPromise = undefined
    mockRadio = ->
      now = new Date().getTime()
      num = Math.random()
      processUpdate('mock', {
        id: '1234567890'
        time: now
        value: num
        })
    radio.enableMock = (millis = 100) ->
      unless mock
        mock = true
        mockPromise = $interval(mockRadio, millis)

    _radioAddr = ''
    _portPath = ''
    _serialPort = undefined

    radio.init = (radioAddr = "0013A20040A580C4", portPath = "/dev/ttyUSB0") ->
      _init = true
      _radioAddr = radioAddr

      _ndl3Radio.close() if _ndl3Radio?
      if requireNode?
        radio = requireNode('ndl3radio')
      else
        radio.enableMock()
        return

      _ndl3Radio = new radio.Radio()

      if _portPath != portPath
        _portPath = portPath
        if _serialPort? # we have an old _serialPort to close
          _serialPort.close( (error) -> initSerialPort() )
        else # we have no _serialPort
          initSerialPort()
      else # portPath hasn't changed, and we have a _serialPort
        registerRadio()

    # make a new _serialPort and register the radio
    initSerialPort = ->
      SerialPort = requireNode("serialport").SerialPort
      _serialPort = new SerialPort(_portPath, baudrate: 57600, false)
      _serialPort.open(registerRadio)

    # register the radio with the serialport
    registerRadio = (error) ->
      if error
        console.log('failed to open: ' + error)

      _ndl3Radio.connectXBee(_radioAddr, _serialPort)
      _ndl3Radio.on('string', (str) ->
        console.log('got string', str)
        )

    radio.close = ->
      if _init
        _ndl3Radio.close() if _ndl3Radio?
        _serialPort.close() if _serialPort?
        _ndl3Radio = undefined
        _serialPort = undefined
        _portPath = ''
        _radioAddr = ''
      _init = false
      return true

    radio.onReceive = (channels..., callback) ->
      return false unless _init # exit if we're not initialized

      for channel in channels
        callbacks[channel] = [] unless callbacks[channel]?
        callbacks[channel].push callback
      return true

    radio.send = (channels..., object) ->
      console.log "called radio.send"
      return false unless _init # exit if we're not initialized
      return false unless object?

      for channel in channels

        if _ndl3Radio
          if channel == 'robotCode'
            _ndl3Radio.send(object, 'code')
          else
            object._channel = channel
            _ndl3Radio.send(object)
        else
          console.log "_ndl3Radio not defined, not sending"

        console.log "radio channel 'chname': sent \nobject"
        .replace(/object/, JSON.stringify(object, null, 4))
        .replace(/chname/, channel)
      return true

    radio.changeGameState = (option = 'ID_CONTROL_SET_AUTON') ->
      id_param = typpo.get_const(option)
      obj = {
        id: id_param
        data: {
          nothing: 0
        }
      }

      cmd = typpo.wrap(typpo.get_type('config_port'), obj)
      buf = new buffer.Buffer(cmd.get_size())
      cmd.write(buf)
      _ndl3Radio.send(buf, 'config')

    return radio
])
