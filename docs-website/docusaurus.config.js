module.exports = {
  title: 'TIR API Docs',
  tagline: 'TIR (Taxonomic Information Registry) API Query Examples',
  url: 'https://data-beta.usgs.gov/tir',
  baseUrl: '/tir/docs/',
  favicon: 'img/favicon.ico',
  organizationName: 'SAS', // Usually your GitHub org/user name.
  projectName: 'tir-api', // Usually your repo name.
  themeConfig: {
    navbar: {
      title: 'TIR API Docs',
      logo: {
        alt: 'TIR Logo',
        src: 'img/logo.png',
      },
      links: [
        {to: 'api_info', label: 'Docs', position: 'left'},
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Using the API',
              to: 'api_info',
            },
            {
              label: 'Examples',
              to: 'examples',
            },
          ],
        },
        {
          title: 'Go To',
          items: [
            {
              label: 'TIR Website',
              href: 'https://www1.usgs.gov/csas/swap/',
            },
            {
              label: 'API',
              href: '..',
            },
          ],
        },
      ],
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          routeBasePath: ''
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
