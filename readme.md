## 基于FLASK的BBS框架
²³³³³³   ₂₃₃₃₃ 

🎃上海某前三985计科导大作业懂的都懂

### 简介

此网站（**暂名为[XXBBS](http://wenweb.ahy1.top/)**）为2019级计算机科学导论小组项目作业，网站定位为**小型校园论坛BBS**

`XXBBS`使用[Flask](https://dormousehole.readthedocs.io/en/latest/)和[Bootstrap](https://getbootstrap.com/)前后端开发，使用[MySQL](https://www.mysql.com/)作为数据库

由部分小组成员@[Yaozhtj](https://github.com/Yaozhtj)@[oscarab](https://github.com/oscarab)  @[sSaltgrey](https://github.com/sSaltgrey) @[crazy-toy](https://github.com/crazy-toy) @[Kururinnpa](https://github.com/Kururinnpa)  和其他小组成员共同完成了此网站

感谢@[oscarab](https://github.com/oscarab)的部署

### 更新日志

+  2020/11/20🔉 **艰难完成登陆注册基本功能**

+ 2020/11/22🧨 **完成footer，選擇了editor-md作爲編輯器**

+ 2020/11/27👓 **完成帖子编辑功能，能不能用看造化吧**

+ 2020/11/30😁 **编辑功能效果还行**

+ 2020/12/05🚕 **完善了首页，完成了搜索功能**

+ 2020/12/07🧒 **完成帖子详情，个人主页**

+ 2020/12/12🍖 **完成回复和提醒功能**

+ 2020/12/15🍳 **无数次的测试完善和改bug**

### 功能(多图警告⚠)

- 首页

    界面如下:

    ![](https://img-blog.csdnimg.cn/20201220201453410.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L1lhb1pob25naGFv,size_16,color_FFFFFF,t_70#pic_center)

- 注册登录功能

    登录界面如下(支持错误提示):

    <img src="https://img-blog.csdnimg.cn/20201220195502972.gif#pic_center"  />

    注册界面如下(支持邮箱验证码发送和错误提示)：

    ![](https://img-blog.csdnimg.cn/2020122020041068.gif#pic_center)

- 发帖功能

    发布帖子使用Markdown编辑器，使用开源的`Editormd`，**虽然此工具已经没人维护，还有些Bug(可参见其[issue](https://github.com/pandao/editor.md/issues))，但功能算是比较好的了**

    ![](https://img-blog.csdnimg.cn/2020122020273694.gif#pic_center)

    编辑框部分功能(**支持跨域上传图片，表情，代码，链接等等**):

    ![](https://img-blog.csdnimg.cn/20201220202735498.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L1lhb1pob25naGFv,size_16,color_FFFFFF,t_70#pic_center)

- 回帖功能(回帖部分也使用了相对简洁的markdown编辑):

    ![在这里插入图片描述](https://img-blog.csdnimg.cn/20201220203335688.gif#pic_center)

- 用户主页

    - 用户可以查看通知(自己的帖子有无新回复)，自己发的帖子，收藏的帖子

    ![在这里插入图片描述](https://img-blog.csdnimg.cn/20201220203757546.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L1lhb1pob25naGFv,size_16,color_FFFFFF,t_70#pic_center)

    - 支持用户的积分制与升级，积分规则：参与发帖或者回复均可增加指定积分，积分累加可升级

    - 支持上传头像

    ![在这里插入图片描述](https://img-blog.csdnimg.cn/20201220215421345.gif#pic_center)

    - 支持积分排行榜

    <img src="https://img-blog.csdnimg.cn/20201220205751940.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L1lhb1pob25naGFv,size_16,color_FFFFFF,t_70#pic_center" alt="在这里插入图片描述" style="zoom: 67%;" />

- 帖子详情页面

    支持`markdown`转`html`渲染

    ![在这里插入图片描述](https://img-blog.csdnimg.cn/20201220210118875.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L1lhb1pob25naGFv,size_16,color_FFFFFF,t_70#pic_center)

    ![在这里插入图片描述](https://img-blog.csdnimg.cn/2020122021104423.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L1lhb1pob25naGFv,size_16,color_FFFFFF,t_70#pic_center)

- 权限功能

    用户组分为`管理员`，`版主`，`普通会员`

    管理员权限最高，可增删用户帖子，移动帖子所属的板块，可禁言版主和普通会员，删除回复

    版主可增删本板块的帖子，移动本版块的帖子，可以禁言普通用户

    ![在这里插入图片描述](https://img-blog.csdnimg.cn/20201220214554426.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L1lhb1pob25naGFv,size_16,color_FFFFFF,t_70#pic_center)

- 支持移动端

    <img src="https://img-blog.csdnimg.cn/20201220220314397.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L1lhb1pob25naGFv,size_5,color_FFFFFF,t_70#pic_center" alt="在这里插入图片描述" style="zoom:25%;" />

<img src="https://img-blog.csdnimg.cn/20201220220314396.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L1lhb1pob25naGFv,size_16,color_FFFFFF,t_70#pic_center" alt="在这里插入图片描述" style="zoom:25%;" />

### At Last

- 第一次用git合作开发，有点不熟悉，水了好多次commit
- 其实还有一些细节未完善，还请大家多多提issue(卑微求star⭐)

