const { defineConfig } = require('@vue/cli-service')
const NodePolyfillPlugin = require("node-polyfill-webpack-plugin")
const CopyWebpackPlugin = require('copy-webpack-plugin')
const path = require('path')

const isDev = process.env.NODE_ENV === 'development'

const outputBaseDir = isDev
    ? `dist/earastellaradmin/`
    : 'dist'

const outputCopyTarget = isDev
    ? path.resolve(__dirname, `dist/earastellaradmin/earastellar`)
    : path.resolve(__dirname, `dist/earastellar`)

module.exports = defineConfig({
  filenameHashing: true,

  publicPath: isDev
      ? `/earastellaradmin/`
      : `/`,

  outputDir: outputBaseDir,

  transpileDependencies: true,
  productionSourceMap: false,

  configureWebpack: {
    plugins: [
      new NodePolyfillPlugin(),

      new CopyWebpackPlugin({
        patterns: [
          {
            from: path.resolve(__dirname, `static/earastellar`),
            to: outputCopyTarget,
            noErrorOnMissing: true
          }
        ]
      })
    ],
    output: {
      filename: 'js/[name].[chunkhash].js'
    }
  }
})
