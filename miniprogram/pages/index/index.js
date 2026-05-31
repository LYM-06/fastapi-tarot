// index.ts
// 获取应用实例
const app = getApp<IAppOption>()
const defaultAvatarUrl = 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0'

// 塔罗牌数据
const tarotCards = [
  {
    name: '魔术师',
    image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Tarot%20card%20The%20Magician%2C%20traditional%20design%2C%20vintage%20style&image_size=square_hd',
    interpretation: '魔术师代表创造力、技能和意志力。你现在拥有实现目标所需的所有资源和能力，只要你相信自己并采取行动，就能成功。'
  },
  {
    name: '女祭司',
    image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Tarot%20card%20The%20High%20Priestess%2C%20traditional%20design%2C%20vintage%20style&image_size=square_hd',
    interpretation: '女祭司代表直觉、潜意识和内在智慧。你需要倾听内心的声音，相信你的直觉，它会引导你找到正确的方向。'
  },
  {
    name: '皇后',
    image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Tarot%20card%20The%20Empress%2C%20traditional%20design%2C%20vintage%20style&image_size=square_hd',
    interpretation: '皇后代表丰饶、母性和创造力。你的生活正处于一个丰收的时期，无论是在事业、感情还是个人成长方面。'
  },
  {
    name: '皇帝',
    image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Tarot%20card%20The%20Emperor%2C%20traditional%20design%2C%20vintage%20style&image_size=square_hd',
    interpretation: '皇帝代表权威、结构和领导力。你需要采取果断的行动，建立清晰的目标和计划，展现你的领导才能。'
  },
  {
    name: '教皇',
    image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Tarot%20card%20The%20Hierophant%2C%20traditional%20design%2C%20vintage%20style&image_size=square_hd',
    interpretation: '教皇代表传统、信仰和指导。你可能需要寻求他人的建议或遵循既定的规则和传统，以获得成功。'
  },
  {
    name: '恋人',
    image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Tarot%20card%20The%20Lovers%2C%20traditional%20design%2C%20vintage%20style&image_size=square_hd',
    interpretation: '恋人代表爱情、选择和和谐。你面临一个重要的选择，需要权衡利弊，做出最适合自己的决定。'
  },
  {
    name: '战车',
    image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Tarot%20card%20The%20Chariot%2C%20traditional%20design%2C%20vintage%20style&image_size=square_hd',
    interpretation: '战车代表胜利、控制和意志力。你需要集中精力，克服障碍，坚定地朝着目标前进。'
  },
  {
    name: '力量',
    image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Tarot%20card%20Strength%2C%20traditional%20design%2C%20vintage%20style&image_size=square_hd',
    interpretation: '力量代表勇气、耐心和内在力量。你拥有克服困难的能力，只要保持冷静和自信，就能战胜挑战。'
  },
  {
    name: '隐士',
    image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Tarot%20card%20The%20Hermit%2C%20traditional%20design%2C%20vintage%20style&image_size=square_hd',
    interpretation: '隐士代表内省、智慧和孤独。你需要花时间独处，反思自己的生活，寻找内在的答案。'
  },
  {
    name: '命运之轮',
    image: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Tarot%20card%20The%20Wheel%20of%20Fortune%2C%20traditional%20design%2C%20vintage%20style&image_size=square_hd',
    interpretation: '命运之轮代表变化、命运和机遇。生活正在发生变化，你需要适应这些变化，抓住新的机遇。'
  }
]

Component({
  data: {
    // 用户信息
    userInfo: {
      avatarUrl: defaultAvatarUrl,
      nickName: '',
    },
    hasUserInfo: false,
    canIUseGetUserProfile: wx.canIUse('getUserProfile'),
    canIUseNicknameComp: wx.canIUse('input.type.nickname'),
    
    // 表单数据
    birthday: '',
    gender: '',
    birthplace: '',
    question: '',
    isFormComplete: false,
    
    // 占卜状态
    isDivining: false,
    showResult: false,
    tarotCard: {
      name: '',
      image: '',
      interpretation: ''
    }
  },
  methods: {
    // 事件处理函数
    bindViewTap() {
      wx.navigateTo({
        url: '../logs/logs',
      })
    },
    onChooseAvatar(e: any) {
      const { avatarUrl } = e.detail
      const { nickName } = this.data.userInfo
      this.setData({
        "userInfo.avatarUrl": avatarUrl,
        hasUserInfo: nickName && avatarUrl && avatarUrl !== defaultAvatarUrl,
      })
    },
    onInputChange(e: any) {
      const nickName = e.detail.value
      const { avatarUrl } = this.data.userInfo
      this.setData({
        "userInfo.nickName": nickName,
        hasUserInfo: nickName && avatarUrl && avatarUrl !== defaultAvatarUrl,
      })
    },
    getUserProfile() {
      // 推荐使用wx.getUserProfile获取用户信息，开发者每次通过该接口获取用户个人信息均需用户确认，开发者妥善保管用户快速填写的头像昵称，避免重复弹窗
      wx.getUserProfile({
        desc: '展示用户信息', // 声明获取用户个人信息后的用途，后续会展示在弹窗中，请谨慎填写
        success: (res) => {
          console.log(res)
          this.setData({
            userInfo: res.userInfo,
            hasUserInfo: true
          })
        }
      })
    },
    
    // 处理生日选择
    onBirthdayChange(e: any) {
      const birthday = e.detail.value
      this.setData({ birthday })
      this.checkFormComplete()
    },
    
    // 处理性别选择
    onGenderChange(e: any) {
      const gender = e.currentTarget.dataset.gender
      this.setData({ gender })
      this.checkFormComplete()
    },
    
    // 处理出生地输入
    onBirthplaceInput(e: any) {
      const birthplace = e.detail.value
      this.setData({ birthplace })
      this.checkFormComplete()
    },
    
    // 处理问题输入
    onQuestionInput(e: any) {
      const question = e.detail.value
      this.setData({ question })
      this.checkFormComplete()
    },
    
    // 检查表单是否完整
    checkFormComplete() {
      const { birthday, gender, birthplace, question } = this.data
      const isComplete = birthday && gender && birthplace && question
      this.setData({ isFormComplete: isComplete })
    },
    
    // 生成基于用户信息的种子值
    generateSeed() {
      const { birthday, gender, birthplace, question } = this.data
      
      // 基于生日生成种子
      const dateParts = birthday.split('-')
      const year = parseInt(dateParts[0])
      const month = parseInt(dateParts[1])
      const day = parseInt(dateParts[2])
      let seed = year + month * 12 + day
      
      // 基于性别调整种子
      if (gender === '女') {
        seed += 1000
      }
      
      // 基于出生地调整种子
      for (let i = 0; i < birthplace.length; i++) {
        seed += birthplace.charCodeAt(i)
      }
      
      // 基于问题调整种子
      for (let i = 0; i < question.length; i++) {
        seed += question.charCodeAt(i)
      }
      
      return seed
    },
    
    // 开始占卜
    startDivination() {
      if (!this.data.isFormComplete) return
      
      this.setData({ isDivining: true })
      
      // 模拟占卜过程
      setTimeout(() => {
        // 使用用户信息生成种子值
        const seed = this.generateSeed()
        
        // 使用种子值生成伪随机数
        const randomIndex = seed % tarotCards.length
        const selectedCard = tarotCards[randomIndex]
        
        this.setData({
          tarotCard: selectedCard,
          showResult: true,
          isDivining: false
        })
      }, 1500)
    },
    
    // 分享结果
    shareResult() {
      const { tarotCard } = this.data
      
      wx.shareAppMessage({
        title: `我的塔罗占卜结果: ${tarotCard.name}`,
        desc: tarotCard.interpretation.substring(0, 50) + '...',
        path: '/pages/index/index',
        imageUrl: tarotCard.image
      })
    },
    
    // 重新占卜
    resetDivination() {
      this.setData({
        // 重置表单数据
        birthday: '',
        gender: '',
        birthplace: '',
        question: '',
        isFormComplete: false,
        
        // 重置占卜状态
        showResult: false,
        tarotCard: {
          name: '',
          image: '',
          interpretation: ''
        }
      })
    }
  },
})
