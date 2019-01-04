/**
 * Copyright 2017, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

const React = require('react');
const PropTypes = require('prop-types');
const {Tooltip, OverlayTrigger} = require('react-bootstrap');

class LayerBtn extends React.Component{
    static propTypes = {
        label: PropTypes.string,
        toggleTOC: PropTypes.func,
        enabled: PropTypes.string
    }
    static defaultProps = {        
        label: "Show layers",
        toggleTOC: () => {},
        enabled: ''
        
    }
    render() {        
        const {label, enabled} = this.props;
        const tooltip = (<Tooltip id={"tooltip-sub-value"} className="disaster">{label}</Tooltip>);
        const active = enabled === 'toc' ? ' active' : '';
        return (
          <OverlayTrigger placement="bottom" overlay={tooltip}>
            <button id="disaster-layer-button" className={"btn btn-primary" + active + " drc"} onClick={() => this.props.toggleTOC()}><i className="glyphicon glyphicon-1-layer"/></button>
          </OverlayTrigger>);
    }
}

module.exports = LayerBtn;
