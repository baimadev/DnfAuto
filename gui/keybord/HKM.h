#ifndef _HKM_
#define _HKM_

#define HKM_FAIL		((DWORD)-1) //ʧ��

//HKMSearchDevice��HKMSearchDevice2��HKMSearchDeviceAll����
#define HDT_ALL		0 //ȫ��ģʽ
#define HDT_KM		1 //����ģʽ
#define HDT_KEY		2 //����ģʽ
#define HDT_MOUSE	3 //���ģʽ

//HKMGetKeyboardMode����ֵ
#define HKT_NONE	0 //�޼���
#define HKT_NORM	1 //��ͨ����
#define HKT_GAME	5 //��Ϸ����

//HKMGetMouseMode����ֵ
#define HMT_NONE	0 //�����
#define HMT_REL		1 //����������
#define HMT_ABS		2 //�����������
#define HMT_RA		3 //����������+�����������
#define HMT_GR		5 //���������Ϸ���
#define HMT_GRA		7 //���������Ϸ���+�����������

//HKMSetMode����
#define HDEMI_MOVE		0x02 //����ƶ���ʽ
#define HDEMI_WHEEL		0x03 //�����ֹ�����ʽ
#define HDEMI_STR		0x04 //����ַ�������
#define HDEMI_SYNC		0x05 //���̡����ͬ����ʽ
#define HDEMI_RND		0x06 //��ʱ�����ʽ
#define HDEMI_DELAY		0x07 //��ʱ��ʽ
#define HDEMI_FUN		0x20 //�����Ĳ������߷���ֵ���ַ�������

#define HDEMM_DEFAULT	0x00 //Ĭ������ƶ���ʽ
#define HDEMM_QUICK		0x01 //�������ƶ�
#define HDEMM_ABS		0x02 //����������ƶ�
#define HDEMM_BASIC		0x04 //����ģʽ��ֻ�������ûʹ����߾������ƶ�������1:1��win10��Dpi��100%ʱʹ��
#define HDEMM_SHIFT		0x00 //����ģʽ����ʼ���٣���������
#define HDEMM_UNIFORM	0x08 //����ģʽ�������ʱ������ٶȣ���HDEMM_DEFAULT�Ͱ���HDEMM_QUICKģʽʱ����HKME_MouseMove��Ч
#define HDEMM_ASSIGN	0x10 //����ģʽ��ʹ��ָ�����ٶȣ���HDEMM_DEFAULT�Ͱ���HDEMM_QUICKģʽʱ����HKME_MouseMove��Ч
#define HDEWM_SIM		0x00 //�����ַ������
#define HDEWM_QUICK		0x01 //�����ֿ��ٹ���
#define HDESM_ANSI		0x00 //����ַ���ANSI���뷽ʽ
#define HDESM_UNICODE	0x01 //����ַ���UNICODE���뷽ʽ
#define HDESM_ANSI2		0x02 //����ַ���ANSI����2��ʽ
#define HDESM_UNICODE2	0x03 //����ַ���UNICODE����2��ʽ
#define HDESM_CLP		0x04 //����ַ���������ճ����ʽ
#define HDEAM_SYNC		0x00 //����������ͬ��
#define HDEAM_KAS		0x01 //���̲����첽
#define HDEAM_MAS		0x02 //�������첽
#define HDERM_UFT		0x00 //��ʱ������ȷֲ�
#define HDERM_LITTLE	0x01 //��ʱ���ƫС�ֲ�
#define HDEDM_NORMAL	0x00 //����������Ϣ
#define HDEDM_WNDMSG	0x01 //��������Ϣ
#define HDEFM_UNICODE	0x00 //�����Ĳ������߷���ֵ���ַ���ʹ��UNICODE����
#define HDEFM_ANSI		0x01 //�����Ĳ������߷���ֵ���ַ���ʹ��ANSI����

//HKMGetKeyboardLEDState����
#define KBD_NUM_LOCK	0 //NumLockָʾ��
#define KBD_CAPS_LOCK	1 //CapsLockָʾ��
#define KBD_SCROLL_LOCK	2 //ScrollLockָʾ��

//HKMIsMouseButtonDown����
#define MSI_LBTN	0 //������
#define MSI_RBTN	1 //����Ҽ�
#define MSI_MBTN	2 //����м�
#define MSI_XB1BTN	3 //���XButton1��
#define MSI_XB2BTN	4 //���XButton2��

//HKMGetDevInfo����
#define DI_TYPE		0x01 //�豸����
#define DI_VERSION	0x02 //�̼��汾
#define DI_RUNTIME	0x03 //����ʱ��
#define DI_POTIME	0x04 //ͨ��ʱ��
#define DI_RSTTIMES	0x06 //��λ����
#define DI_RUNSTATE	0x07 //����״̬
#define DI_VID		0x08 //USB VID
#define DI_PID		0x09 //USB PID
#define DI_DEVVER	0x0A //USB�豸�汾

//HKMCheckPressedKeys����
#define CKM_CHS			0x01 //��鰴�������ذ������ĵ���Ϣ
#define CKM_MOUSE		0x02 //��鰴�������ذ��������µ�������Ϣ
#define CKM_ANSI		0x04 //��鰴�������ص��ַ���ʹ��ANSI����

//DPIģʽ,HKMOpen��HKMOpen2����
#define DPIM_PHYSICAL	0 //ÿ����ʾ��DPI��֪��windowsϵͳ��win8.1��ʼ֧�ִ�ģʽ��win8.1��ǰ��Ч��ϵͳDPI��֪
#define DPIM_SYSTEM		1 //ϵͳDPI��֪
#define DPIM_UNAWARE	2 //��DPI��֪
#define DPIM_DISABLE	3 //DPI������,���ͷź�ִ��DPI�����̣����������������������������win8.1��ǰ��ϵͳ��ϵͳDPI��100%ʱ���ߵ�ǰ�����ĵ�DPI��֪��ϵͳDPI��֪ʱ��������������win8.1��win8.1�Ժ��ϵͳ��������ʾ��DPI��100%ʱ��ǰ�����ĵ�DPI��֪��ÿ����ʾ��DPI��֪ʱ����������
#define DPIM_CURRENT	4 //��ǰ�����ĵ�DPI��֪

//����豸�ַ������
#define DS_MFR		0x01 //������
#define DS_PROD		0x02 //��Ʒ��

//�豸����״̬
#define DRS_NOCONNECT	((DWORD)-1) //δ����
#define DRS_PREPARE		0x00 //׼��
#define DRS_WORK		0x01 //����
#define DRS_EDIT		0x02 //�༭
#define DRS_DISABLE		0x03 //��ֹ����

//��ʱ��λģʽ
#define DRM_DEV			0x00 //�豸��λ
#define DRM_KM			0x01 //������긴λ

//�豸ָʾ��ģʽ
#define DLM_DEFAULT		0x00 //Ĭ��
#define DLM_LIGHT		0x01 //����
#define DLM_DARK		0x02 //����
#define DLM_NORST		0x08 //ģʽ����λ

//USB�豸������Ϣ
#define UD_IGNOREINT	0x10000
#define UD_IGNORESTR	((LPCWSTR)0x01)

//����USB�豸������Ϣģʽ
#define SDM_NORMAL		0x00 //ȡ���ڴ�ģʽ
#define SDM_RAM			0x01 //�ڴ�ģʽ��USB�豸������Ϣ���浽�ڴ�
#define SDM_FLASH		0x02 //����ģʽ��USB�豸������Ϣ���浽����

//HKMGetError����ֵ
#define HE_SUCCESS			0x0000 //�ɹ�
#define HE_FAIL				0xE001 //ʧ��
#define HE_INVALIDPARAM		0xE002 //��Ч�Ĳ���
#define HE_INVALIDPOINTER	0xE003 //��Ч��ָ��
#define HE_INVALIDOBJECT	0xE004 //��Ч�Ķ���
#define HE_INVALIDINITVALUE	0xE005 //��Ч�ĳ�ʼ��ֵ
#define HE_INVALIDDATA		0xE006 //��Ч������
#define HE_DATAOVERFLOW		0xE007 //����̫��
#define HE_STROVERFLOW		0xE008 //�ַ���̫��
#define HE_INSUFFICIENTBUF	0xE009 //��������̫С
#define HE_NOSUPPORT		0xE00A //��֧��
#define HE_OBJALREADYEXIST	0xE00B //�����Ѵ���
#define HE_SYSERR			0xE00C //ϵͳ����
#define HE_OPENDEVFAIL		0xE020 //���豸ʧ��
#define HE_COMMFAIL			0xE021 //ͨ��ʧ��
#define HE_NOACCESS			0xE022 //�޷���Ȩ��
#define HE_TIMEOUT			0xE023 //��ʱ
#define HE_RUNAPPFAIL		0xE024 //����Ӧ��ʧ��
#define HE_OVERLIMIT		0xE025 //��������
#define HE_GETDPIFAIL		0xE026 //��ȡDPI��Ϣʧ��
#define HE_GETDATAFAIL		0xE027 //��ȡ����ʧ��
#define HE_DEVFAIL			0xE028 //�豸ʧ��
#define HE_DEVTIMEOUT		0xE029 //�豸��ʱ

#ifdef __cplusplus
extern "C" {
#endif

DECLSPEC_IMPORT DWORD WINAPI HKMGetVersion(void);
DECLSPEC_IMPORT DWORD WINAPI HKMSearchDevice(DWORD dwVid, DWORD dwPid, DWORD dwDeviceType);
DECLSPEC_IMPORT DWORD WINAPI HKMSearchDevice2(DWORD dwVid, DWORD dwPid, DWORD dwSN, DWORD dwDeviceType);
DECLSPEC_IMPORT LPDWORD WINAPI HKMSearchDeviceAll(DWORD dwVid, DWORD dwPid, DWORD dwDeviceType);
DECLSPEC_IMPORT LPVOID WINAPI HKMOpen(DWORD dwDeviceId, DWORD dwDpiMode);
DECLSPEC_IMPORT LPVOID WINAPI HKMOpen2(DWORD dwDeviceId1, DWORD dwDeviceId2, DWORD dwDpiMode);
DECLSPEC_IMPORT BOOL WINAPI HKMIsOpen(LPVOID lpHKMData, DWORD dwFlags);
DECLSPEC_IMPORT BOOL WINAPI HKMClose(LPVOID lpHKMData);
DECLSPEC_IMPORT DWORD WINAPI HKMGetDevInfo(LPVOID lpHKMData,DWORD dwIndex,BOOL bMouse);
DECLSPEC_IMPORT LPWSTR WINAPI HKMGetDevString(LPVOID lpHKMData,DWORD dwIndex,BOOL bMouse,LPDWORD lpLength);
DECLSPEC_IMPORT DWORD WINAPI HKMGetSerialNumber(LPVOID lpHKMData, BOOL bMouse);
DECLSPEC_IMPORT DWORD WINAPI HKMGetKeyboardMode(LPVOID lpHKMData);
DECLSPEC_IMPORT DWORD WINAPI HKMGetMouseMode(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMIsKeyBusy(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMIsMouseBusy(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMIsKeyDown(LPVOID lpHKMData,LPCWSTR lpKeyName);
DECLSPEC_IMPORT BOOL WINAPI HKMIsMouseButtonDown(LPVOID lpHKMData,DWORD dwIndex);
DECLSPEC_IMPORT BOOL WINAPI HKMGetKeyboardLEDState(LPVOID lpHKMData, DWORD dwIndex);
DECLSPEC_IMPORT BOOL WINAPI HKMGetCursorPos(LPVOID lpHKMData,LPLONG lpX, LPLONG lpY);
DECLSPEC_IMPORT DWORD WINAPI HKMGetCursorPos2(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMSetMode(LPVOID lpHKMData, DWORD dwIndex, DWORD dwMode);
DECLSPEC_IMPORT BOOL WINAPI HKMSetKeyInterval(LPVOID lpHKMData, DWORD dwMinTime, DWORD dwMaxTime);
DECLSPEC_IMPORT BOOL WINAPI HKMSetMouseInterval(LPVOID lpHKMData, DWORD dwMinTime, DWORD dwMaxTime);
DECLSPEC_IMPORT BOOL WINAPI HKMSetAbsMouseScrnRes(LPVOID lpHKMData, long lWidth, long lHeight);
DECLSPEC_IMPORT BOOL WINAPI HKMSetMousePosPrecision(LPVOID lpHKMData, DWORD dwPrecision);
DECLSPEC_IMPORT BOOL WINAPI HKMSetMouseSpeed(LPVOID lpHKMData, DWORD dwMouseSpeed);
DECLSPEC_IMPORT BOOL WINAPI HKMSetMouseMoveTimeout(LPVOID lpHKMData, DWORD dwTimeout);
DECLSPEC_IMPORT BOOL WINAPI HKMSetMousePosMaxOffset(LPVOID lpHKMData, DWORD dwOffset);
DECLSPEC_IMPORT BOOL WINAPI HKMKeyPress(LPVOID lpHKMData, LPCWSTR lpKeyName);
DECLSPEC_IMPORT BOOL WINAPI HKMKeyDown(LPVOID lpHKMData, LPCWSTR lpKeyName);
DECLSPEC_IMPORT BOOL WINAPI HKMKeyUp(LPVOID lpHKMData, LPCWSTR lpKeyName);
DECLSPEC_IMPORT BOOL WINAPI HKMMoveTo(LPVOID lpHKMData, long nX, long nY);
DECLSPEC_IMPORT BOOL WINAPI HKMMoveR(LPVOID lpHKMData, long nX, long nY);
DECLSPEC_IMPORT BOOL WINAPI HKMMoveR2(LPVOID lpHKMData, long nX, long nY);
DECLSPEC_IMPORT BOOL WINAPI HKMMoveRP(LPVOID lpHKMData, long nX, long nY);
DECLSPEC_IMPORT BOOL WINAPI HKMLeftClick(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMRightClick(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMMiddleClick(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMXBtn1Click(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMXBtn2Click(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMLeftDoubleClick(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMRightDoubleClick(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMMiddleDoubleClick(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMXBtn1DoubleClick(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMXBtn2DoubleClick(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMLeftDown(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMRightDown(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMMiddleDown(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMXBtn1Down(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMXBtn2Down(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMLeftUp(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMRightUp(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMMiddleUp(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMXBtn1Up(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMXBtn2Up(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMMouseWheel(LPVOID lpHKMData, long nCount);
DECLSPEC_IMPORT BOOL WINAPI HKMMouseWheelP(LPVOID lpHKMData, long nCount);
DECLSPEC_IMPORT BOOL WINAPI HKMReleaseKeyboard(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMReleaseMouse(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMOutputString(LPVOID lpHKMData, LPCWSTR lpString);
DECLSPEC_IMPORT BOOL WINAPI HKMDelayRnd(LPVOID lpHKMData, DWORD dwMinTime, DWORD dwMaxTime);
DECLSPEC_IMPORT LPWSTR WINAPI HKMCheckPressedKeys(DWORD dwFlags, LPDWORD lpLength);
DECLSPEC_IMPORT BOOL WINAPI HKMVerifyUserData(LPVOID lpHKMData, LPCWSTR lpString, BOOL bMouse);
DECLSPEC_IMPORT DWORD WINAPI HKMVerifyUserData2(LPVOID lpHKMData, LPCWSTR lpString, BOOL bMouse);
DECLSPEC_IMPORT BOOL WINAPI HKMSetResetMode(LPVOID lpHKMData, DWORD dwMode, BOOL bMouse);
DECLSPEC_IMPORT BOOL WINAPI HKMSetResetTime(LPVOID lpHKMData, DWORD dwTime, BOOL bMouse);
DECLSPEC_IMPORT BOOL WINAPI HKMSetLightMode(LPVOID lpHKMData, DWORD dwMode, BOOL bMouse);
DECLSPEC_IMPORT BOOL WINAPI HKMSetDevDescInfo(LPVOID lpHKMData,DWORD dwVID,DWORD dwPID,DWORD dwDeviceVersion,LPCWSTR lpManufacturer,LPCWSTR lpProduct,DWORD dwMode,BOOL bMouse);
DECLSPEC_IMPORT DWORD WINAPI HKMGetError(LPVOID lpHKMData);
DECLSPEC_IMPORT BOOL WINAPI HKMIsOSMouseAccelerateEnabled(void);
DECLSPEC_IMPORT BOOL WINAPI HKMEnableOSMouseAccelerate(BOOL bEnable, BOOL bSave);
DECLSPEC_IMPORT int WINAPI HKMGetOSMouseSpeed(void);
DECLSPEC_IMPORT BOOL WINAPI HKMSetOSMouseSpeed(int nSpeed, BOOL bSave);
DECLSPEC_IMPORT BOOL WINAPI HKMFreeData(LPVOID lpData);
DECLSPEC_IMPORT DWORD WINAPI HKMGetDataCount(LPVOID lpData);
DECLSPEC_IMPORT DWORD WINAPI HKMGetDataUnitInt(LPVOID lpData, DWORD dwIndex);

#ifdef __cplusplus
}
#endif

#endif //_HKM_
