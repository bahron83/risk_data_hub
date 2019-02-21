var webpackConfig = require('./webpack.config.js');
var path = require("path");
var LoaderOptionsPlugin = require("webpack/lib/LoaderOptionsPlugin");
var ParallelUglifyPlugin = require("webpack-parallel-uglify-plugin");
var DefinePlugin = require("webpack/lib/DefinePlugin");
//var OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin');
var NormalModuleReplacementPlugin = require("webpack/lib/NormalModuleReplacementPlugin");
const extractThemesPlugin = require('./MapStore2/themes.js').extractThemesPlugin;
//var CopyWebpackPlugin = require('copy-webpack-plugin');

webpackConfig.plugins = [
    /*new CopyWebpackPlugin([
        { from: path.join(__dirname, 'node_modules', 'bootstrap', 'less'), to: path.join(__dirname, "web", "client", "dist", "bootstrap", "less") }
    ]),*/
    new LoaderOptionsPlugin({
        debug: false,
        options: {
            postcss: {
                plugins: [
                  require('postcss-prefix-selector')({prefix: '.RiskDataHubClient', exclude: ['.RiskDataHubClient', '.ms2', '[data-ms2-container]']})
                ]
            },
            context: __dirname
        }
    }),
    new DefinePlugin({
        "__DEVTOOLS__": false
    }),
    new DefinePlugin({
      'process.env': {
        'NODE_ENV': '"production"'
      }
    }),
    new NormalModuleReplacementPlugin(/leaflet$/, path.join(__dirname, "MapStore2", "web", "client", "libs", "leaflet")),
    new NormalModuleReplacementPlugin(/openlayers$/, path.join(__dirname, "MapStore2", "web", "client", "libs", "openlayers")),
    new NormalModuleReplacementPlugin(/cesium$/, path.join(__dirname, "MapStore2", "web", "client", "libs", "cesium")),
    new NormalModuleReplacementPlugin(/proj4$/, path.join(__dirname, "MapStore2", "web", "client", "libs", "proj4")),    
    new NormalModuleReplacementPlugin(/map\/leaflet\/Feature/, path.join(__dirname, "js", "ms2Override", "LeafletFeature.jsx")),
    new NormalModuleReplacementPlugin(/map\/leaflet\/Layer/, path.join(__dirname, "js", "ms2Override", "LeafletLayer.jsx")),
    new NormalModuleReplacementPlugin(/map\/leaflet\/plugins\/WMSLayer/, path.join(__dirname, "js", "ms2Override", "LeafletWMSLayer.js")),
    //new NormalModuleReplacementPlugin(/reducers\/layers$/, path.join(__dirname, "js", "ms2Override", "layersReducer.js")),
    new NormalModuleReplacementPlugin(/reducers\/map$/, path.join(__dirname, "js", "ms2Override", "mapreducer.js")),
    new NormalModuleReplacementPlugin(/map\/leaflet\/snapshot\/GrabMap/, path.join(__dirname, "js", "ms2Override", "LGrabMap.jsx")),
    new NormalModuleReplacementPlugin(/map\/openlayers\/Map/, path.join(__dirname, "js", "ms2Override", "components", "OlMap.jsx")),
    new NormalModuleReplacementPlugin(/map\/openlayers\/DrawSupport/, path.join(__dirname, "js", "ms2Override", "components", "DrawSupport.jsx")),
    new NormalModuleReplacementPlugin(/DockPanel.jsx/, path.join(__dirname, "js", "ms2Override", "components", "DockPanel.jsx")),
    new NormalModuleReplacementPlugin(/PanelHeader.jsx/, path.join(__dirname, "js", "ms2Override", "components", "PanelHeader.jsx")),
    //new NormalModuleReplacementPlugin(/selectors\/layers/, path.join(__dirname, "js", "ms2Override", "selectors", "layers.js")),
    new NormalModuleReplacementPlugin(/client\/selectors\/layer/, path.join(__dirname, "js", "ms2Override", "layersSelector.js")),
    new NormalModuleReplacementPlugin(/VectorStyle.js/, path.join(__dirname, "js", "ms2Override", "components", "VectorStyle.js")),
    new NormalModuleReplacementPlugin(/SideCard.jsx/, path.join(__dirname, "js", "ms2Override", "components", "SideCard.jsx")),
    new NormalModuleReplacementPlugin(/SideGrid.jsx/, path.join(__dirname, "js", "ms2Override", "components", "SideGrid.jsx")),
    new NormalModuleReplacementPlugin(/ToggleButton.jsx/, path.join(__dirname, "js", "ms2Override", "components", "ToggleButton.jsx")),
    new NormalModuleReplacementPlugin(/ResizableModal.jsx/, path.join(__dirname, "js", "ms2Override", "components", "ResizableModal.jsx")),
    new ParallelUglifyPlugin({
        uglifyES: {
            sourceMap: false,
            compress: {warnings: false},
            mangle: true
        }
    }),
    extractThemesPlugin/*,
    new OptimizeCssAssetsPlugin({
        cssProcessorOptions: { discardComments: { removeAll: true } }
      })*/
];
webpackConfig.devtool = undefined;

// this is a workaround for this issue https://github.com/webpack/file-loader/issues/3
// use `__webpack_public_path__` in the index.html when fixed
//webpackConfig.output.publicPath = "/RiskDataHubClient/dist/";
webpackConfig.output.publicPath = "/static/js";

module.exports = webpackConfig;
