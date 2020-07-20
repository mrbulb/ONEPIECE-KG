## Changelog

###v1.2.3(21/07/2020)

**Improvements**

- 将截止至2020.07.21之前发行的**所有**生命卡中实体关系数据**标注完成**，增加的数据包括：庞克哈萨德、德雷斯罗萨、佐乌、蛋糕岛。
- 去除了N-Triples数据中的重复项。
- 根据生命卡官方网站的[订正表](https://one-piece.com/vivre/revision.php)，修正了生命卡中的相应数据(NOTE：关系数据那边更新起来比较复杂，暂时没有去更新)
- 优化了可视化页面，希望缓解由于结点增加导致的视觉效果上的拥挤

### v1.2.2 (05/04/2020)

**Improvements**

- 增加了标注的实体关系数据，增加的数据包括：鱼人岛。

**New Features**

- 在可视化方面，增加了新的特性：当鼠标移动悬停到某个结点/文本的时候，会显示和相邻结点的关系(之前是只有连线表示)。([#3](https://github.com/mrbulb/ONEPIECE-KG/issues/3))

### v1.2.1 (12/03/2020)

**Improvements**

- 对可视化的关系数据进行了实体对齐，去掉了重复的部分。
- 增加了标注的实体关系数据，增加的数据包括：香波地群岛、女儿岛、海底大监狱、顶上战争、ASL回忆篇。

**New Features**

- 为可视化页面增加了统计访问信息的代码，可以通过百度统计来查看网站的访问情况。
- 在每个角色的信息框中，增加了对应头像图片的展示，图片来源于[此网站](https://one-piece.com/vivre/list2.php)。

### v1.2.0 (28/02/2020)

**Improvements**

- 去掉了之前只能在Microsoft Edge浏览器打开可视化页面的限制，目前经过测试可以在Chrome，Firefox等主流浏览器上打开。
- 增加了标注的实体关系数据，增加的数据包括：加雅岛、空岛、七水之都、司法岛、恐怖三桅帆船。

**New Features**

- 为项目增加了 `README.md` 文件。
- 增加了项目的报告文件 `docs/report.md`。
- 增加了 `docs/CHANGELOG.md`。
- 为项目增加了[GitHub Pages](https://mrbulb.github.io/ONEPIECE-KG/)，目前主要展示实体关系可视化的部分。([#1](https://github.com/mrbulb/ONEPIECE-KG/issues/1))
