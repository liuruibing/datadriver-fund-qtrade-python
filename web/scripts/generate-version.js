import fs from 'fs';
import { createRequire } from 'module';

// 使用require来读取package.json以避免ES模块导入问题
const require = createRequire(import.meta.url);
const packageJson = require('../package.json');
const version = packageJson.version;

// 生成版本文件到public目录下version文件中
const VERSION_FILE_NAME = 'version-build';
const package_version = version;
const versionString = `${package_version}.${new Date().getTime()}`;

try {
  fs.writeFileSync(`public/${VERSION_FILE_NAME}`, versionString);
  console.log('Version file generated successfully:', versionString);
} catch (error) {
  console.error('Error generating version file:', error);
  process.exit(1);
}
