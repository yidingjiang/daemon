/**
 * A component representing a scalar sensor.
 * Props:
 *   id: a unique id string
 *   value: the speed, from 0 to 100.
 */

import React from 'react';
import {ProgressBar} from 'react-bootstrap';
import NameEdit from './NameEdit';

var Motor = React.createClass({
  propTypes: {
    name: React.PropTypes.string,
    value: React.PropTypes.number
  },
  render() {
    return (
    <div style={{overflow: 'auto'}}>
      <div style={{overflow: 'auto', width: '100%'}}>
        <h4 style={{float: 'left'}}><NameEdit name={this.props.name} /><small> Scalar Sensor</small></h4>
        <h4 style={{float: 'right'}}> {this.props.value} </h4>
      </div>
      <ProgressBar now={this.props.value}></ProgressBar>
    </div>
    );
  }
});

export default Motor;
