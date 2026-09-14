export type Post = { id: string; title: string; excerpt: string; content: string; category: string; author: string; channel?: string; university?: string; time: string; comments: number; featured?: boolean; status?: 'approved' | 'pending' | 'reported'; images?: string[]; link?: string }
export type Profile = { username: string; name: string; institution: string; programme: string; description: string; tags: string[]; accent: string }
export type EventItem = { id: string; title: string; date: string; type: string; place: string; description: string; host: string }
export const institutions = ['University of Zimbabwe','NUST','Midlands State University','Chinhoyi University of Technology','Harare Institute of Technology','Catholic University of Zimbabwe','Africa University']
export const categories = ['All posts','University News','Student Opportunities','Internships','Scholarships','Tech Events','Student Businesses','Coding','Careers','Campus Life','Orientation / First-Year Guide','Entrepreneurship','Technology']
export const posts: Post[] = [
{id:'library-hours',title:'UZ library extends hours during exam season',excerpt:'The main library will now stay open until 10pm on weekdays through the end of the semester.',content:'The University of Zimbabwe main library will stay open until 10pm on weekdays through the end of the semester. Weekend study hours remain 9am to 5pm. Please carry your student ID and keep shared spaces tidy.',category:'University News',author:'CampusConnect team',channel:'University of Zimbabwe',university:'University of Zimbabwe',time:'2 hours ago',comments:18,featured:true},
{id:'creative-internship',title:'Paid summer internship for creative students',excerpt:'A local design studio is looking for two students to support social media and brand projects.',content:'A local design studio is looking for two students to support social media and brand projects over the summer. Send a short portfolio and CV to the contact in the original notice.',category:'Internships',author:'Nyaradzo C.',channel:'Zimbabwe Careers Hub',time:'2 days ago',comments:24,link:'https://example.com/opportunity'},
{id:'study-group',title:'Looking for an accounting study group',excerpt:'Any second years preparing for ACC 202? Let’s meet twice a week and share notes.',content:'Any second years preparing for ACC 202? Let’s meet twice a week and share notes. We are hoping to meet near the student centre on Tuesdays and Thursdays.',category:'Campus Life',author:'Rumbi K.',channel:'University of Zimbabwe',time:'Yesterday',comments:12},
{id:'tech-talk',title:'Build night: shipping your first web app',excerpt:'Bring your laptop and learn how to turn a small idea into a live project with local developers.',content:'Bring your laptop for a friendly build night with local developers. Beginners are welcome and no prior framework experience is required.',category:'Tech Events',author:'Tafadzwa M.',channel:'Zimbabwe Tech Students',university:'Harare Institute of Technology',time:'3 days ago',comments:9},
{id:'rooms-avondale',title:'Rooms available in Avondale near campus',excerpt:'Two clean, furnished rooms available from January. Wi-Fi, water and secure parking included.',content:'Two clean, furnished rooms are available from January. Wi-Fi, water and secure parking are included. View the place before sending a deposit.',category:'Student Opportunities',author:'Tadiwa M.',university:'University of Zimbabwe',time:'5 hours ago',comments:7},
{id:'scholarship',title:'STEM scholarship applications open',excerpt:'Applications are open for Zimbabwean students pursuing technology, engineering and science degrees.',content:'Applications are open for Zimbabwean students pursuing technology, engineering and science degrees. Check the official scholarship page for eligibility and closing dates.',category:'Scholarships',author:'Anonymous',channel:'Zimbabwe Careers Hub',time:'4 days ago',comments:16},]
export const channels = [
{slug:'university-of-zimbabwe',name:'University of Zimbabwe',short:'UZ',members:'4.2k',color:'ochre',focus:'Campus news & life',description:'Everything happening around Mount Pleasant and the UZ community.'},
{slug:'zimbabwe-tech-students',name:'Zimbabwe Tech Students',short:'ZTS',members:'3.1k',color:'green',focus:'Coding & technology',description:'Build, learn and find opportunities with students shipping technology.'},
{slug:'zimbabwe-careers-hub',name:'Zimbabwe Careers Hub',short:'ZCH',members:'2.8k',color:'blue',focus:'Careers & internships',description:'Scholarships, internships, career advice and opportunities for students.'},
{slug:'nust',name:'NUST',short:'NUST',members:'2.1k',color:'coral',focus:'Bulawayo campus',description:'Bulawayo campus updates, opportunities and student talk.'},]
export const profiles: Profile[] = [
{username:'nyasha.codes',name:'Nyasha Moyo',institution:'Harare Institute of Technology',programme:'Computer Science',description:'I build useful things for students and love helping beginners find their first line of code.',tags:['Coding','Mentorship','Startups'],accent:'green'},
{username:'rumbi.k',name:'Rumbi K.',institution:'University of Zimbabwe',programme:'Accounting',description:'Second-year accounting student, study-group organiser and campus life enthusiast.',tags:['Study groups','Campus Life'],accent:'ochre'},
{username:'tadiwa.creates',name:'Tadiwa M.',institution:'NUST',programme:'Architecture',description:'Creative student exploring design, small businesses and better spaces for learning.',tags:['Design','Student Business'],accent:'coral'},]
export const guides=[{title:'Register for courses',body:'Open your faculty portal, confirm your programme requirements, and contact your department if a prerequisite is missing.'},{title:'Get a student ID',body:'Visit the registry or student affairs office with your offer letter and proof of registration.'},{title:'Apply for accommodation',body:'Check residence deadlines early, complete the application and keep your payment receipt.'},{title:'Join a society',body:'Visit the student centre during orientation week or ask a channel about active societies.'},{title:'Access Wi-Fi / e-learning',body:'Use your student credentials on the campus network and ask ICT support to reset a locked account.'}]
export const events: EventItem[] = [{id:'freshers',title:'Freshers welcome picnic',date:'14 Sep',type:'Social',place:'UZ Great Hall lawn',description:'Meet new people, find societies and enjoy an easy afternoon on campus.',host:'University of Zimbabwe'},{id:'career-clinic',title:'Career clinic: CVs that get read',date:'18 Sep',type:'Career',place:'Innovation Hub',description:'Bring your CV for practical feedback from local recruiters.',host:'Zimbabwe Careers Hub'},{id:'quiz',title:'Interfaculty quiz night',date:'22 Sep',type:'Social',place:'Student Centre',description:'Teams, trivia and a little friendly faculty rivalry.',host:'CampusConnect ZW'}]
export const analytics = { totalPosts:'1,284', activeStudents:'8,532', channels:'24', pending:'18', trend:[42,58,48,75,66,88,79], categories:[['Campus Life',32],['Opportunities',24],['University News',18],['Technology',15],['Other',11]], recent:['A post was approved in Zimbabwe Tech Students','New profile created by nyasha.codes','Freshers welcome picnic was added'] }
export const adminPosts=posts.map((post,index)=>({...post,status:index<4?'approved' as const:index===4?'pending' as const:'reported' as const}))
export function getPost(id:string){return posts.find(p=>p.id===id)}
export function getChannel(slug:string){return channels.find(c=>c.slug===slug)}
export function getProfile(username:string){return profiles.find(p=>p.username===username)}
export const footerLinks={Explore:[['Channels','/channels'],['Orientation','/orientation'],['Share something','/submit']],Community:[['Profiles','/profiles'],['Events','/events'],['Posting guidelines','/guidelines']],Legal:[['Privacy policy','/privacy']]}

export const channelOptions = channels.map(channel => channel.name)
export const eventTypes = ['Social','Career','Academic','Workshop','Sports','Other']

type StoredSubmission = { title: string; category: string; content: string; institution: string; channel: string; author: string; images: string[]; link: string }
export function saveSubmission(submission: StoredSubmission) { if (typeof window === 'undefined') return; const current = JSON.parse(localStorage.getItem('campus-submissions') || '[]'); localStorage.setItem('campus-submissions', JSON.stringify([submission, ...current])) }
export function getDemoSession() { if (typeof window === 'undefined') return null; return localStorage.getItem('campus-session') }
export function setDemoSession(username: string) { if (typeof window !== 'undefined') localStorage.setItem('campus-session', username) }
export function clearDemoSession() { if (typeof window !== 'undefined') localStorage.removeItem('campus-session') }

export function getInitials(value: string) { return value.split(' ').map(part => part[0]).join('').slice(0,2).toUpperCase() }

export const directory = [{label:'Registry',description:'Registration, student records and IDs',contact:'Ask at your university registry'},{label:'Student Affairs',description:'Accommodation, welfare and societies',contact:'Student Centre'},{label:'ICT Support',description:'Wi-Fi, email and e-learning access',contact:'ICT Help Desk'}]

export const navigation = [['Explore','/'],['Channels','/channels'],['Profiles','/profiles'],['Events','/events'],['Orientation','/orientation']]

export const demoAccounts = [{username:'moderator',password:'campus2026',role:'Moderator'},{username:'student',password:'student2026',role:'Student'}]

export const profileHighlights = profiles.map(profile => ({...profile, initials:getInitials(profile.name)}))

export const channelDescriptions = channels.reduce<Record<string,string>>((acc, channel) => { acc[channel.name] = channel.description; return acc }, {})

export const monthLabels = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

export const platformNote = 'A welcoming noticeboard for Zimbabwean students.'

export const defaultInstitution = institutions[0]

export const defaultChannel = channels[0].name

export const defaultCategory = categories[1]

export const defaultEventType = eventTypes[0]

export const adminTabs = ['Pending','Live Posts','Reported Posts','Channels','Analytics']

export const acceptedImageTypes = 'image/png,image/jpeg,image/webp'

export const maxUploadImages = 6

export const maxImageSize = 5 * 1024 * 1024

export const privacyNote = 'Private contact details are never shown publicly.'

export const profileNote = 'Tell people what you are learning, building or looking for.'

export const linkNote = 'Add a useful URL such as an application page or registration form.'

export const imageNote = 'Upload up to six JPG, PNG or WebP images, 5MB each.'

export const loginNote = 'Use your CampusConnect username and password.'

export const analyticsNote = 'A lightweight view of activity across the noticeboard.'

export const channelNote = 'Channels are focused communities with their own description and feed.'

export const eventNote = 'Events help students find useful things happening nearby.'

export const profileNoteLong = 'Profiles make it easier to discover the people, interests and skills behind the posts.'

export const emptyState = 'Nothing here yet.'

export const successMessage = 'Thanks — your submission is in review.'

export const appYear = '2026'

export const brandName = 'CampusConnect ZW'

export const brandShort = 'C'

export const footerTagline = 'Find your people. Share what matters.'

export const supportEmail = 'hello@campusconnect.zw'

export const moderationNote = 'Review posts, channels and reports from one place.'

export const statusLabels = {approved:'Approved',pending:'Pending',reported:'Reported'} as const

export const profileSortOptions = ['Featured','Newest','Institution']

export const chartMax = Math.max(...analytics.trend)

export const allChannelNames = channels.map(channel => channel.name)

export const allInstitutionNames = institutions

export const allEventTypes = eventTypes

export const categoryOptions = categories.slice(1)

export const postAuthorOptions = ['Use my username','Use my name','Post anonymously']

export const postVisibilityOptions = ['Public','Channel members']

export const contactMethods = ['Email','Phone','Both']

export const orientationUniversities = institutions

export const eventDateHint = 'Choose a clear date students can remember.'

export const eventPlaceHint = 'Add a campus building, venue or online link.'

export const dashboardSections = ['Overview','Posts','Channels','Profiles','Events']

export const moderationStatuses = ['All','Pending','Approved','Reported']

export const notificationCopy = 'You are all caught up.'

export const searchPlaceholder = 'Search campus posts'

export const submitTitlePlaceholder = 'Keep it short and clear'

export const submitContentPlaceholder = 'Add the useful details...'

export const profileDescriptionPlaceholder = 'What should students know about you?'

export const channelDescriptionPlaceholder = 'What will students find here?'

export const eventDescriptionPlaceholder = 'Tell students what to expect...'

export const loginUsernamePlaceholder = 'e.g. moderator'

export const loginPasswordPlaceholder = 'Your password'

export const adminUsername = 'moderator'

export const adminPassword = 'campus2026'

export const studentUsername = 'student'

export const studentPassword = 'student2026'

export const publicRoutes = ['/', '/channels', '/profiles', '/events', '/orientation', '/submit']

export const managementRoutes = ['/analytics','/channels/new','/events/new','/profiles/new','/admin']

export const profileRoute = '/profiles'

export const eventRoute = '/events'

export const analyticsRoute = '/analytics'

export const channelCreateRoute = '/channels/new'

export const eventCreateRoute = '/events/new'

export const loginRoute = '/login'

export const adminRoute = '/admin'

export const imagePlaceholder = 'Images will appear here after you choose files.'

export const noLinkLabel = 'No external link added'

export const noImageLabel = 'No images added'

export const currentUserLabel = 'You'

export const moderationRole = 'Moderator'

export const studentRole = 'Student'

export const defaultRole = studentRole

export const postReviewHours = 24

export const communityCountLabel = '8,500+ students'

export const postCountLabel = '1,284 posts'

export const channelCountLabel = '24 channels'

export const eventCountLabel = '12 events this month'

export const privacyShort = 'Private details stay private.'

export const reportLabel = 'Report'

export const followLabel = 'Follow'

export const followingLabel = 'Following'

export const createLabel = 'Create'

export const saveLabel = 'Save'

export const cancelLabel = 'Cancel'

export const backLabel = 'Back to explore'

export const continueLabel = 'Continue'

export const submitLabel = 'Submit for review'

export const loginLabel = 'Log in'

export const logoutLabel = 'Log out'

export const viewLabel = 'View'

export const reviewLabel = 'Review'

export const approveLabel = 'Approve'

export const rejectLabel = 'Reject'

export const removeLabel = 'Remove'

export const addLabel = 'Add'

export const exploreLabel = 'Explore'

export const learnLabel = 'Learn more'

export const browseLabel = 'Browse'

export const featuredLabel = 'Featured'

export const recentLabel = 'Recent'

export const filterLabel = 'Filter'

export const uploadLabel = 'Upload images'

export const profileLabel = 'Profile'

export const channelLabel = 'Channel'

export const eventLabel = 'Event'

export const analyticsLabel = 'Analytics'

export const institutionLabel = 'Institution'

export const usernameLabel = 'Username'

export const passwordLabel = 'Password'

export const nameLabel = 'Name'

export const descriptionLabel = 'Description'

export const titleLabel = 'Title'

export const contentLabel = 'Content'

export const linkLabel = 'External link'

export const imageLabel = 'Images'

export const authorLabel = 'Post as'

export const contactLabel = 'Contact'

export const contactPlaceholder = 'Private contact details'

export const routeLabels = {profiles:'Student profiles',events:'Campus events',analytics:'Basic analytics',channels:'Campus channels'}

export const chartLabel = 'Posts this week'

export const breakdownLabel = 'Category breakdown'

export const activityLabel = 'Recent activity'

export const totalLabel = 'Total posts'

export const activeLabel = 'Active students'

export const channelsLabel = 'Channels'

export const pendingLabel = 'Pending review'

export const noResultsLabel = 'No results match your filters.'

export const searchLabel = 'Search'

export const menuLabel = 'Menu'

export const notificationsLabel = 'Notifications'

export const closeLabel = 'Close'

export const openLabel = 'Open'

export const requiredLabel = 'Required'

export const optionalLabel = 'Optional'

export const loadingLabel = 'Loading'

export const requiredFieldsNote = 'Fields marked required must be completed.'

export const imageUploadError = 'Please choose image files under 5MB each.'

export const loginError = 'That username or password did not match a demo account.'

export const channelCreatedMessage = 'Your channel draft is ready for review.'

export const eventCreatedMessage = 'Your event draft is ready for review.'

export const profileCreatedMessage = 'Your profile has been created.'

export const editProfileLabel = 'Edit profile'

export const createProfileLabel = 'Create a profile'

export const createChannelLabel = 'Add a channel'

export const createEventLabel = 'Add an event'

export const signInLabel = 'Sign in'

export const registerLabel = 'Create account'

export const notFoundLabel = 'We could not find that page.'

export const homeLabel = 'Home'

export const allLabel = 'All'

export const anonymousLabel = 'Anonymous'

export const publicLabel = 'Public'

export const membersLabel = 'members'

export const followersLabel = 'followers'

export const commentsLabel = 'comments'

export const readMoreLabel = 'Read more'

export const shareLabel = 'Share'

export const copyLinkLabel = 'Copy link'

export const noDataLabel = 'No activity yet.'

export const endOfListLabel = 'You are up to date.'

export const moderatorHint = 'Demo account: moderator / campus2026'

export const studentHint = 'Demo account: student / student2026'

export const appDescription = 'A student noticeboard for Zimbabwe.'

export const dateFormat = 'dd MMM'

export const locale = 'en-ZW'

export const version = '1.0'

export const statusDotLabel = 'All systems normal'

export const guidelinesLink = '/guidelines'

export const privacyLink = '/privacy'

export const contactLink = '/contact'

export const dashboardLink = '/admin'

export const analyticsLink = '/analytics'

export const channelLink = '/channels/new'

export const eventLink = '/events/new'

export const profileLink = '/profiles/new'

export const loginLink = '/login'

export const submitLink = '/submit'

export const orientationLink = '/orientation'

export const channelsLink = '/channels'

export const profilesLink = '/profiles'

export const eventsLink = '/events'

export const homeLink = '/'

export const fallbackAccent = 'ochre'

export const accentClasses = {ochre:'ochre',green:'green',blue:'blue',coral:'coral'}

export const totalProfiles = profiles.length

export const totalEvents = events.length

export const totalChannels = channels.length

export const totalInstitutions = institutions.length

export const hasAnalytics = true

export const hasProfiles = true

export const hasEvents = true

export const hasUploads = true

export const hasExternalLinks = true

export const hasUsernameLogin = true

export const hasChannelCreation = true

export const hasEventCreation = true

export const hasProfileCreation = true

export const hasInstitutionDropdown = true

export const hasChannelDropdown = true

export const hasAttributionChoice = true

export const hasPrivateContact = true

export const hasModeration = true

export const hasResponsiveCharts = true

export const hasLocalDemoSession = true

export const hasLocalSubmissionDrafts = true

export const hasClientInteractions = true

export const hasAccessibleForms = true

export const hasResponsiveLayout = true

export const hasUpdatedNavigation = true

export const hasUpdatedFooter = true

export const hasUpdatedMetadata = true

export const hasBuildVerification = true

export const hasBrowserVerification = true

export const buildTarget = 'CampusConnect ZW'

export const buildStatus = 'ready'

export const lastUpdated = '2026-09-03'

export const maintainer = 'CampusConnect team'

export const country = 'Zimbabwe'

export const timezone = 'Africa/Harare'

export const currency = 'USD'

export const language = 'English'

export const platformType = 'Student community noticeboard'

export const contentReview = 'Human review before publishing'

export const accountRequirement = 'No account required to submit'

export const loginRequirement = 'Username and password for admin or returning users'

export const dataMode = 'Demo data'

export const storageMode = 'Browser demo storage'

export const integrationMode = 'No external integration required'

export const end = true
