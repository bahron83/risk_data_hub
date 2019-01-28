const PropTypes = require('prop-types');
/**
 * Copyright 2015, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

const React = require('react');
var {connect} = require('react-redux');
const L = require('leaflet');
const {isEqual} = require('lodash');
const {clickOnMap} = require('../../MapStore2/web/client/actions/map');
const {zoomInOut} = require('../actions/disaster');

const VectorUtils = require('../../MapStore2/web/client/utils/leaflet/Vector');

const coordsToLatLngF = function(coords) {
    return new L.LatLng(coords[1], coords[0], coords[2]);
};

const coordsToLatLngs = function(coords, levelsDeep, coordsToLatLng) {
    var latlngs = [];
    var len = coords.length;
    for (let i = 0, latlng; i < len; i++) {
        latlng = levelsDeep ?
                coordsToLatLngs(coords[i], levelsDeep - 1, coordsToLatLng) :
                (coordsToLatLng || this.coordsToLatLng)(coords[i]);

        latlngs.push(latlng);
    }

    return latlngs;
};
// Create a new Leaflet layer with custom icon marker or circleMarker
const getPointLayer = function(pointToLayer, geojson, latlng, options) {
    if (pointToLayer) {
        return pointToLayer(geojson, latlng);
    }
    return VectorUtils.pointToLayer(latlng, geojson, options.style);
};

const geometryToLayer = function(geojson, options) {

    var geometry = geojson.type === 'Feature' ? geojson.geometry : geojson;
    var coords = geometry ? geometry.coordinates : null;
    var layers = [];
    var pointToLayer = options && options.pointToLayer;
    var latlng;
    var latlngs;
    var i;
    var len;
    let coordsToLatLng = options && options.coordsToLatLng || coordsToLatLngF;

    if (!coords && !geometry) {
        return null;
    }

    const style = options.style && options.style[geometry.type] || options.style;
    let layer;
    switch (geometry.type) {
    case 'Point':
        latlng = coordsToLatLng(coords);
        layer = getPointLayer(pointToLayer, geojson, latlng, options);
        layer.msId = geojson.id;
        return layer;
    case 'MultiPoint':
        for (i = 0, len = coords.length; i < len; i++) {
            latlng = coordsToLatLng(coords[i]);
            layer = getPointLayer(pointToLayer, geojson, latlng, options);
            layer.msId = geojson.id;
            layers.push(layer);
        }
        return new L.FeatureGroup(layers);

    case 'LineString':
        latlngs = coordsToLatLngs(coords, geometry.type === 'LineString' ? 0 : 1, coordsToLatLng);
        layer = new L.Polyline(latlngs, style);
        layer.msId = geojson.id;
        return layer;
    case 'MultiLineString':
        latlngs = coordsToLatLngs(coords, geometry.type === 'LineString' ? 0 : 1, coordsToLatLng);
        for (i = 0, len = latlngs.length; i < len; i++) {
            layer = new L.Polyline(latlngs[i], style);
            layer.msId = geojson.id;
            if (layer) {
                layers.push(layer);
            }
        }
        return new L.FeatureGroup(layers);
    case 'Polygon':
        latlngs = coordsToLatLngs(coords, geometry.type === 'Polygon' ? 1 : 2, coordsToLatLng);
        layer = new L.Polygon(latlngs, style);
        layer.msId = geojson.id;
        return layer;
    case 'MultiPolygon':
        latlngs = coordsToLatLngs(coords, geometry.type === 'Polygon' ? 1 : 2, coordsToLatLng);
        for (i = 0, len = latlngs.length; i < len; i++) {
            layer = new L.Polygon(latlngs[i], style);
            layer.msId = geojson.id;
            if (layer) {
                layers.push(layer);
            }
        }
        return new L.FeatureGroup(layers);
    case 'GeometryCollection':
        for (i = 0, len = geometry.geometries.length; i < len; i++) {
            layer = geometryToLayer({
                geometry: geometry.geometries[i],
                type: 'Feature',
                properties: geojson.properties
            }, options);

            if (layer) {
                layers.push(layer);
            }
        }
        return new L.FeatureGroup(layers);

    default:
        throw new Error('Invalid GeoJSON object.');
    }
};

class Feature extends React.Component {
    static propTypes = {
        msId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        type: PropTypes.string,
        styleName: PropTypes.string,
        properties: PropTypes.object,
        container: PropTypes.object, // TODO it must be a L.GeoJSON
        geometry: PropTypes.object, // TODO check for geojson format for geometry
        style: PropTypes.object,
        onClick: PropTypes.func,
        options: PropTypes.object        
    };

    adjustProps(feature) {         
        if(feature && 'value' in feature.properties) {
            const { rules } = feature && feature.style || null;
            if(rules) {            
                for(let rule of rules) {                 
                    if(feature.properties.value != null) {
                        if (feature.properties.value < rule.max_value) {                                                         
                            const style = {...feature.style, fillColor: rule.fillColor}                            
                            return {...feature, style}
                        }                        
                    }                
                }             
            }                                        
        }        
        return feature;        
    }

    componentDidMount() {
        if (this.props.container && this.props.geometry) {
            this._tooltip = L.popup({closeButton: false, offset: [85, 35], className: 'disaster-map-tooltip', autoPan: false});                        
            this.createLayer(this.adjustProps(this.props));                                      
        }
    }    

    componentWillReceiveProps(newProps) {
        if (!isEqual(newProps.properties, this.props.properties) || !isEqual(newProps.geometry, this.props.geometry) || !isEqual(newProps.style, this.props.style)) {            
            this.props.container.removeLayer(this._layer);            
            this.createLayer(this.adjustProps(newProps)); 
        }
    }

    shouldComponentUpdate(nextProps) {        
        return !isEqual(nextProps.properties, this.props.properties) || !isEqual(nextProps.geometry, this.props.geometry);
    }

    componentWillUnmount() {
        if (this._layer) {
            this.props.container.removeLayer(this._layer);
        }
    }    

    render() {        
        return null;
    }

    /*onClick() {
        const {properties, onClick, getFeatureInfoEnabled} = this.props;
        if (onClick && !getFeatureInfoEnabled) {
            onClick(properties.href, properties.geom);
        }
    }*/
    

    isMarker = (props) => {
        return props.styleName === "marker" || (props.style && (props.style.iconUrl || props.style.iconGlyph));
    };

    createLayer = (props) => {
        this._layer = geometryToLayer({
            type: props.type,
            geometry: props.geometry,
            properties: props.properties,
            msId: props.msId
        }, {
            style: props.style,
            pointToLayer: !this.isMarker(props) ? function(feature, latlng) {
                return L.circleMarker(latlng, props.style || {
                    radius: 5,
                    color: "red",
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0
                });
            } : null
        }
        );
        props.container.addLayer(this._layer);

        this._layer.on('click', () => {
            if (props.onClick) {
                props.onClick(this.props.properties.href, this.props.properties.geom);
            }
        });

        this._layer.on('mouseover', (event) => {            
            this._layer.setStyle({weight: 4, 'className': "admin"});
            this._tooltip.setLatLng(event.latlng)
                .setContent(`Zoom to ${this.props.properties && this.props.properties.label}`);
            this._layer.addLayer(this._tooltip);            
        });

        this._layer.on('mouseout', () => {
            this._layer.removeLayer(this._tooltip);
            this._layer.setStyle({weight: 1, 'className': null});
        });

        this._layer.on('mousemove', (event) => {
            this._tooltip.setLatLng(event.latlng);
        });
    };
}

module.exports = connect((state)=> ({getFeatureInfoEnabled: state.controls && state.controls.info && state.controls.info.enabled }), {onClick: zoomInOut, clickOnMap})(Feature);
