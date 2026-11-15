import {Config} from '@remotion/cli/config';

// Remotion sources live in remotion/ (Ever Present's layout). Stills only at M3; low concurrency while the GPU and
// CPU are shared with other projects' renders.
Config.setEntryPoint('remotion/src/index.ts');
Config.setPublicDir('remotion/public');
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(92);
Config.setConcurrency(2);
