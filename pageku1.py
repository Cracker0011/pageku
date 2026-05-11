import requests
import base64
import json
import uuid
import time
import hashlib
import os
import re
import random
import string
import struct
import threading
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

COOLDOWN_SECONDS = 7 * 60

def clear():
    os.system("clear" if os.name == "posix" else "cls")	

def ENCPASS_KATANA(pw):
    t = int(time.time())
    did = str(uuid.uuid4())
    try:
        r = requests.get('https://graph.facebook.com/pwd_key_fetch', headers={'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 10; M2010J19CG MIUI/V12.0.3.0.QJFEUXM) [FBAN/MobileAdsManagerAndroid;FBAV/462.0.0.53.107;FBBV/881830739;FBRV/0;FBPN/com.facebook.adsmanager;FBLC/id_ID;FBMF/Xiaomi;FBBD/POCO;FBDV/M2010J19CG;FBSV/10;FBCA/arm64-v8a:armeabi-v7a:armeabi;FBDM/{density=2.4,width=1080,height=2149};FB_FW/1;]'}, params={'access_token': '438142079694454|fc0a7caa49b192f64f6f5a6d9643bb28', 'device_id': did, 'version': '2'}).json()
        pk, kid = r.get("public_key"), r.get("key_id")
        if not pk: return f"#PWD_FB4A:0:{t}:{pw}"
        rk, iv = get_random_bytes(32), get_random_bytes(12)
        ek = PKCS1_v1_5.new(RSA.import_key(pk)).encrypt(rk)
        ac = AES.new(rk, AES.MODE_GCM, nonce=iv)
        ac.update(str(t).encode())
        ep, tg = ac.encrypt_and_digest(pw.encode())
        payload = base64.b64encode(bytes([1, kid]) + iv + struct.pack("<h", len(ek)) + ek + tg + ep).decode()
        return f"#PWD_FB4A:2:{t}:{payload}"
    except Exception as e:
        return f"#PWD_FB4A:0:{t}:{pw}"


def random_name():
    word = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 9))).capitalize()
    suffix = ''.join(random.choices(string.ascii_lowercase, k=random.randint(2, 4)))
    digits = ''.join(random.choices(string.digits, k=5))
    return f"{word}{suffix}.{digits}"


def extract_access_token(text):
    m = re.search(r'access_token[^A-Za-z0-9]+(EAA[A-Za-z0-9_]+)', text)
    if m:
        return m.group(1)
    return None


def extract_new_profile_id(text, original_uid):
    for m in re.finditer(r'"(?:profile_id|uid|id)"[^0-9]+(\d{10,17})', text):
        candidate = m.group(1)
        if candidate != str(original_uid):
            return candidate
    return None


class CreatePage:
    def __init__(self, uid, pw, totp_seed):
        self.uid = uid
        self.pw = pw
        self.totp_seed = totp_seed
        self.r = requests.Session()
        self.current_timestamp = int(time.time())
        self.device_id = str(uuid.uuid4())
        self.timer = str(round(time.time()))
        self.url = "https://b-graph.facebook.com/graphql"
        self.android_device = "android-%s" % hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
        self.encpass = ENCPASS_KATANA(self.pw)
        self.accesstoken = ""
        self.context = ""
        self.otpcode = ""
        self.name = random_name()
        self.head = {
            "X-Fb-Request-Analytics-Tags": '{"network_tags":{"product":"350685531728","request_category":"graphql","purpose":"fetch","retry_attempt":"0"},"application_tags":"graphservice"}',
            "X-Fb-Rmd": "state=URL_ELIGIBLE",
            "Priority": "u=0",
            "X-Fb-Device-Group": "2101",
            "X-Fb-Integrity-Machine-Id": "NM4Bav6UK5w5YiZFtO22bofN",
            "X-Zero-Eh": hashlib.md5(f"{self.device_id}{self.current_timestamp}".encode()).hexdigest(),
            "User-Agent": "[FBAN/FB4A;FBAV/555.0.0.49.59;FBBV/926293029;FBDM/{density=1.5,width=1280,height=720};FBLC/id_ID;FBRV/0;FBCR/PSN;FBMF/samsung;FBBD/samsung;FBPN/com.facebook.katana;FBDV/SM-G960N;FBSV/9;FBOP/1;FBCA/x86_64:arm64-v8a;]",
            "X-Graphql-Request-Purpose": "fetch",
            "X-Zero-F-Device-Id": str(uuid.uuid4()),
            "X-Tigon-Is-Retry": "False",
            "X-Zero-State": "unknown",
            "X-Graphql-Client-Library": "graphservice",
            "X-Fb-Sim-Hni": "51000",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Fb-Net-Hni": "51000",
            "Authorization": "OAuth 350685531728|62f8ce9f74b12f84c123cc23437a4a32",
            "X-Meta-Zca": "empty_token",
            "App-Scope-Id-Header": str(uuid.uuid4()),
            "X-Fb-Connection-Type": "WIFI",
            "X-Meta-Usdid": f"{str(uuid.uuid4())}.{self.current_timestamp}.MEUCIQC1Q5Wpq0xh36yu13b1rex-fRcvH0jOSTsGJtvTqbmqqgIgO58pKRH4tCoM5xUep_-HnGZA9Vhu5dadwQhS7zHLS1A",
            "X-Fb-Http-Engine": "Tigon/Liger",
            "X-Fb-Client-Ip": "True",
            "X-Fb-Server-Cluster": "True",
            "X-Fb-Conn-Uuid-Client": "ubrIZdAUGJfiMxn1ClPPXQ==",
        }
        self.head3 = {
            "X-Fb-Request-Analytics-Tags": '{"network_tags":{"product":"350685531728","request_category":"graphql","purpose":"fetch","retry_attempt":"0"},"application_tags":"graphservice"}',
            "X-Fb-Rmd": "state=URL_ELIGIBLE",
            "Priority": "u=0",
            "User-Agent": "[FBAN/FB4A;FBAV/555.0.0.49.59;FBBV/926293029;FBDM/{density=1.5,width=1280,height=720};FBLC/id_ID;FBRV/0;FBCR/PSN;FBMF/samsung;FBBD/samsung;FBPN/com.facebook.katana;FBDV/SM-G960N;FBSV/9;FBOP/1;FBCA/x86_64:arm64-v8a;]",
            "X-Fb-Friendly-Name": "FbBloksAppRootQuery-com.bloks.www.unified.profile.creation",
            "X-Zero-F-Device-Id": str(uuid.uuid4()),
            "X-Fb-Integrity-Machine-Id": "NM4Bav6UK5w5YiZFtO22bofN",
            "X-Graphql-Request-Purpose": "fetch",
            "X-Fb-Device-Group": "2101",
            "X-Tigon-Is-Retry": "False",
            "X-Graphql-Client-Library": "graphservice",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Zero-Eh": hashlib.md5(f"{self.device_id}{self.current_timestamp}".encode()).hexdigest(),
            "X-Fb-Net-Hni": "51000",
            "X-Fb-Sim-Hni": "51000",
            "Authorization": f"OAuth {self.accesstoken}",
            "App-Scope-Id-Header": str(uuid.uuid4()),
            "X-Fb-Connection-Type": "WIFI",
            "X-Meta-Zca": "empty_token",
            "X-Meta-Usdid": f"{str(uuid.uuid4())}.{self.current_timestamp}.MEUCIQC1Q5Wpq0xh36yu13b1rex-fRcvH0jOSTsGJtvTqbmqqgIgO58pKRH4tCoM5xUep_-HnGZA9Vhu5dadwQhS7zHLS1A",
            "X-Fb-Http-Engine": "Tigon/Liger",
            "X-Fb-Client-Ip": "True",
            "X-Fb-Server-Cluster": "True",
            "X-Fb-Conn-Uuid-Client": "Ot/2iNbqk2kiyMj1kGgpKw==",
        }
        self.head1 = self.head.copy()
        self.head2 = self.head3.copy()

    def get_2fa_token(self):
        try:
            clean_seed = self.totp_seed.replace(" ", "")
            self.otpcode = self.r.get(f"https://2fa.live/tok/{clean_seed}").json()["token"]
            print(f"[✓] 2FA token berhasil didapat: {self.otpcode}")
            return self.otpcode
        except Exception as e:
            print(f"[✗] Error saat get 2FA token: {str(e)}")
            return None

    def _update_head2_token(self):
        self.head2["Authorization"] = f"OAuth {self.accesstoken}"
        self.head3["Authorization"] = f"OAuth {self.accesstoken}"

    def login(self):
        challenge_nonce = base64.b64encode(os.urandom(24)).decode()[:32].replace('+', '/').replace('=', '')
        self.head1.update({"X-Fb-Friendly-Name": "FbBloksActionRootQuery-com.bloks.www.bloks.caa.login.async.send_login_request"})
        params = {
            "method": "post",
            "pretty": "false",
            "format": "json",
            "server_timestamps": "true",
            "locale": "id_ID",
            "purpose": "fetch",
            "fb_api_req_friendly_name": "FbBloksActionRootQuery-com.bloks.www.bloks.caa.login.async.send_login_request",
            "fb_api_caller_class": "graphservice",
            "client_doc_id": "119940804217734265480409226803",
            "fb_api_client_context": '{"is_background":false}',
            "variables": json.dumps({
                "params": {
                    "params": json.dumps({
                        "params": json.dumps({
                            "client_input_params": {
                                "blocked_uids": [],
                                "aac": json.dumps({"aac_init_timestamp": self.current_timestamp - 30, "aaccs": "BdXcPrvuOzmpJcWnj04v53V5Y62d4WVZTBr-nbt0u4s", "aacjid": str(uuid.uuid4())}),
                                "sim_phones": [],
                                "aymh_accounts": [],
                                "network_bssid": None,
                                "secure_family_device_id": str(uuid.uuid4()),
                                "attestation_result": {
                                    "keyHash": "9a8588c58f3018cb654f2d2f6354c4b7b351273ae6e8322aba92644cac764a5c",
                                    "data": base64.b64encode(json.dumps({"challenge_nonce": challenge_nonce, "username": self.uid}).encode()).decode(),
                                    "signature": "MEUCIFFu56NsvenjeUYF7JShmL6p2xk8cwU7+Lf2JfA2cl1/AiEAmHx54w1fk+Ev7hukY9f10agKxj94Pi1bEORQqC4ahp8="
                                },
                                "has_granted_read_contacts_permissions": 0,
                                "auth_secure_device_id": "",
                                "has_whatsapp_installed": 1,
                                "si_device_param_network_info": {
                                    "active_subscriptions_info": None,
                                    "default_subscription_info": {
                                        "network_type": None, "is_data_roaming": 1, "is_esim": None, "is_gsm_roaming": 0,
                                        "is_sim_sms_capable": None, "is_mobile_data_enabled": 1, "sim_carrier_id": -1,
                                        "sim_carrier_id_name": None, "sim_state": 5, "sim_operator": "51000",
                                        "sim_operator_name": "PT+Pasifik+Satelit+Nusantara+(ACeS)", "signal_strength": None,
                                        "group_id_level_1": None, "network_operator": "51000"
                                    },
                                    "is_airplane_mode": 1, "is_active_network_cellular": 0, "is_device_sms_capable": 1, "sim_count": 1, "is_wifi": 1
                                },
                                "password": self.encpass,
                                "sso_token_map_json_string": "",
                                "block_store_machine_id": None,
                                "cloud_trust_token": None,
                                "event_flow": "login_manual",
                                "password_contains_non_ascii": "false",
                                "sim_serials": [],
                                "client_known_key_hash": "",
                                "sso_accounts_auth_data": [],
                                "encrypted_msisdn": "",
                                "has_granted_read_phone_permissions": 0,
                                "app_manager_id": "null",
                                "should_show_nested_nta_from_aymh": 0,
                                "device_id": str(uuid.uuid4()),
                                "zero_balance_state": "init",
                                "login_attempt_count": 1,
                                "machine_id": "NM4Bav6UK5w5YiZFtO22bofN",
                                "flash_call_permission_status": {"READ_PHONE_STATE": "DENIED", "READ_CALL_LOG": "DENIED", "ANSWER_PHONE_CALLS": "DENIED"},
                                "accounts_list": [{"uid": self.uid, "credential_type": "abandoned_ar", "metadata": {"contactpoint": self.uid}, "token": ""}],
                                "gms_incoming_call_retriever_eligibility": "not_eligible",
                                "family_device_id": str(uuid.uuid4()),
                                "fb_ig_device_id": [],
                                "device_emails": [],
                                "try_num": 1,
                                "lois_settings": {"lois_token": ""},
                                "event_step": "home_page",
                                "headers_infra_flow_id": "",
                                "openid_tokens": {},
                                "contact_point": self.uid
                            },
                            "server_params": {
                                "should_trigger_override_login_2fa_action": 0, "is_from_logged_out": 0,
                                "should_trigger_override_login_success_action": 0, "login_credential_type": "none",
                                "server_login_source": "login", "waterfall_id": str(uuid.uuid4()),
                                "two_step_login_type": "one_step_login", "login_source": "Login",
                                "is_platform_login": 0, "pw_encryption_try_count": 1, "login_entry_point": "logged_out",
                                "INTERNAL__latency_qpl_marker_id": 36707139, "is_from_aymh": 0,
                                "offline_experiment_group": "caa_iteration_v6_perf_fb_2", "is_from_landing_page": 0,
                                "left_nav_button_action": "NONE", "password_text_input_id": "75j6lj:115",
                                "is_from_empty_password": 0, "is_from_msplit_fallback": 0,
                                "ar_event_source": "login_home_page", "username_text_input_id": "75j6lj:114",
                                "layered_homepage_experiment_group": None, "device_id": str(uuid.uuid4()),
                                "login_surface": "login_home", "INTERNAL__latency_qpl_instance_id": 43255632700843,
                                "reg_flow_source": "login_home_native_integration_point", "is_caa_perf_enabled": 1,
                                "credential_type": "password", "is_from_password_entry_page": 0, "caller": "gslr",
                                "family_device_id": str(uuid.uuid4()), "is_from_assistive_id": 0,
                                "x_app_device_signals": {"MACHINE_ID": "aftC2QABAAGV_jtBSDKxKIJL9kA-", "DEVICE_ID": self.android_device},
                                "access_flow_version": "pre_mt_behavior", "is_from_logged_in_switcher": 0
                            }
                        })
                    }),
                    "bloks_versioning_id": "d1583f026cccd22345fea8de656bb1d8162dabcca3249d6a0610be47545ec31a",
                    "app_id": "com.bloks.www.bloks.caa.login.async.send_login_request"
                },
                "scale": "1.5",
                "nt_context": {
                    "using_white_navbar": True, "styles_id": "6100e7e89411ccf67ace027cedecd84f",
                    "pixel_ratio": 1.5, "is_push_on": True, "debug_tooling_metadata_token": None,
                    "is_flipper_enabled": False,
                    "theme_params": [{"value": ["three_neutral_gray"], "design_system_name": "XMDS"}, {"value": [], "design_system_name": "FDS"}],
                    "bloks_version": "d1583f026cccd22345fea8de656bb1d8162dabcca3249d6a0610be47545ec31a"
                }
            }),
            "fb_api_analytics_tags": '["GraphServices"]',
            "client_trace_id": str(uuid.uuid4()),
        }
        resking = self.r.post(self.url, headers=self.head1, data=params)
        restext = resking.text
        direct_token = extract_access_token(restext)
        if direct_token and "two_fac_redirect" not in restext and "two_step_verification" not in restext and "redirection_to_two_fac" not in restext:
            print(f"[✓] Login berhasil tanpa 2FA.")
            self.accesstoken = direct_token
            self._update_head2_token()
            return True
        if "two_fac_redirect" in restext or "two_step_verification" in restext or "redirection_to_two_fac" in restext:
            print("[!] Akun memerlukan verifikasi 2FA...")
            m = re.search(r'two_step_verification_context.{0,300}?([A-Za-z0-9_\-]{80,})', restext)
            if m:
                self.context = m.group(1)
                token = self.get_2fa_token()
                if not token:
                    print(f"[✗] {self.uid} | Gagal dapat token 2FA.")
                    return False
                return self.verification2fa()
            else:
                print(f"[✗] {self.uid} | Gagal ekstrak context 2FA.")
                return False

        print(f"[✗] {self.uid} | Tidak ada access_token maupun 2FA di response login.")
        return False

    def verification2fa(self):
        self.head1.update({"X-Fb-Friendly-Name": "FbBloksActionRootQuery-com.bloks.www.two_step_verification.verify_code.async"})
        params = {
            "method": "post",
            "pretty": "false",
            "format": "json",
            "server_timestamps": "true",
            "locale": "id_ID",
            "purpose": "fetch",
            "fb_api_req_friendly_name": "FbBloksActionRootQuery-com.bloks.www.two_step_verification.verify_code.async",
            "fb_api_caller_class": "graphservice",
            "client_doc_id": "119940804217734265480409226803",
            "fb_api_client_context": '{"is_background":false}',
            "variables": json.dumps({
                "params": {
                    "params": json.dumps({
                        "params": json.dumps({
                            "client_input_params": {
                                "auth_secure_device_id": "",
                                "block_store_machine_id": None,
                                "code": self.otpcode,
                                "should_trust_device": 1,
                                "family_device_id": str(uuid.uuid4()),
                                "device_id": str(uuid.uuid4()),
                                "cloud_trust_token": None,
                                "network_bssid": None,
                                "machine_id": "NM4Bav6UK5w5YiZFtO22bofN"
                            },
                            "server_params": {
                                "INTERNAL__latency_qpl_marker_id": 36707139,
                                "device_id": None,
                                "spectra_reg_login_data": None,
                                "challenge": "totp",
                                "INTERNAL__latency_qpl_instance_id": 43357426300202,
                                "two_step_verification_context": self.context,
                                "flow_source": "two_factor_login"
                            }
                        })
                    }),
                    "bloks_versioning_id": "d1583f026cccd22345fea8de656bb1d8162dabcca3249d6a0610be47545ec31a",
                    "app_id": "com.bloks.www.two_step_verification.verify_code.async"
                },
                "scale": "1.5",
                "nt_context": {
                    "using_white_navbar": True, "styles_id": "6100e7e89411ccf67ace027cedecd84f",
                    "pixel_ratio": 1.5, "is_push_on": True, "debug_tooling_metadata_token": None,
                    "is_flipper_enabled": False,
                    "theme_params": [{"value": ["three_neutral_gray"], "design_system_name": "XMDS"}, {"value": [], "design_system_name": "FDS"}],
                    "bloks_version": "d1583f026cccd22345fea8de656bb1d8162dabcca3249d6a0610be47545ec31a"
                }
            }),
            "fb_api_analytics_tags": '["GraphServices"]',
            "client_trace_id": str(uuid.uuid4()),
        }
        resking = self.r.post(self.url, headers=self.head1, data=params)
        restext = resking.text

        token = extract_access_token(restext)
        if token:
            print(f"[✓] 2FA berhasil. Access token didapat.")
            self.accesstoken = token
            self._update_head2_token()
            return True
        else:
            print(f"[✗] {self.uid} | Gagal dapat access_token dari response 2FA.")
            return False

    def unifedprofile(self):
        self.head2.update({"X-Fb-Friendly-Name": "FbBloksAppRootQuery-com.bloks.www.unified.profile.creation"})
        params = {
            "method": "post", "pretty": "false", "format": "json", "server_timestamps": "true",
            "locale": "id_ID", "purpose": "fetch",
            "fb_api_req_friendly_name": "FbBloksAppRootQuery-com.bloks.www.unified.profile.creation",
            "fb_api_caller_class": "graphservice", "client_doc_id": "10537346116379767315688237631",
            "fb_api_client_context": '{"is_background":false}',
            "variables": json.dumps({
                "params": {
                    "params": json.dumps({"server_params": {"design_variant": "promode_spotlight_neutral", "source": "BOOKMARK_CREATE_ACTION", "tracking_id": str(uuid.uuid4())}}),
                    "bloks_versioning_id": "d1583f026cccd22345fea8de656bb1d8162dabcca3249d6a0610be47545ec31a",
                    "app_id": "com.bloks.www.unified.profile.creation"
                },
                "scale": "1.5", "use_native_entrypoint_for_stars_on_reels": True,
                "nt_context": {
                    "using_white_navbar": True, "styles_id": "6100e7e89411ccf67ace027cedecd84f",
                    "pixel_ratio": 1.5, "is_push_on": True, "debug_tooling_metadata_token": None,
                    "is_flipper_enabled": False,
                    "theme_params": [{"value": ["three_neutral_gray"], "design_system_name": "XMDS"}, {"value": [], "design_system_name": "FDS"}],
                    "bloks_version": "d1583f026cccd22345fea8de656bb1d8162dabcca3249d6a0610be47545ec31a"
                }
            }),
            "fb_api_analytics_tags": '["surfaces.fb.GraphServiceEmitter","GraphServices"]',
            "client_trace_id": str(uuid.uuid4()),
        }
        resking = self.r.post(self.url, headers=self.head2, data=params)

    def additionalprofile(self):
        self.head2.update({"X-Fb-Friendly-Name": "FbBloksAppRootQuery-com.bloks.www.additional.profile.plus.creation"})
        params = {
            "method": "post", "pretty": "false", "format": "json", "server_timestamps": "true",
            "locale": "id_ID", "purpose": "fetch",
            "fb_api_req_friendly_name": "FbBloksAppRootQuery-com.bloks.www.additional.profile.plus.creation",
            "fb_api_caller_class": "graphservice", "client_doc_id": "10537346116379767315688237631",
            "fb_api_client_context": '{"is_background":false}',
            "variables": json.dumps({
                "params": {
                    "params": json.dumps({"server_params": {
                        "referrer": "bookmark_create_action", "creation_source": "android",
                        "use_updated_unified_creation_copy_for_name_screen": 1, "variant": 8, "screen": "name",
                        "unified_entrypoint_tracker_id": str(uuid.uuid4()), "show_secondary_button": 1,
                        "unified_creation_source": "BOOKMARK_CREATE_ACTION",
                        "value_prop_config": {
                            "disclaimer-type": "page_terms", "disclaimer-below-button": 0,
                            "body": "Berdasarkan+pilihan+Anda,+Halaman+memiliki+fitur+yang+Anda+perlukan.",
                            "headline": "Mulai+dengan+Halaman", "include-secondary-button": 1,
                            "onboarding-items": ["audience_intent_tools", "audience_intent_insights", "audience_intent_reach_more", "audience_intent_multiple_owners"]
                        }
                    }}),
                    "bloks_versioning_id": "d1583f026cccd22345fea8de656bb1d8162dabcca3249d6a0610be47545ec31a",
                    "app_id": "com.bloks.www.additional.profile.plus.creation"
                },
                "scale": "1.5", "use_native_entrypoint_for_stars_on_reels": True,
                "nt_context": {
                    "using_white_navbar": True, "styles_id": "6100e7e89411ccf67ace027cedecd84f",
                    "pixel_ratio": 1.5, "is_push_on": True, "debug_tooling_metadata_token": None,
                    "is_flipper_enabled": False,
                    "theme_params": [{"value": ["three_neutral_gray"], "design_system_name": "XMDS"}, {"value": [], "design_system_name": "FDS"}],
                    "bloks_version": "d1583f026cccd22345fea8de656bb1d8162dabcca3249d6a0610be47545ec31a"
                }
            }),
            "fb_api_analytics_tags": '["surfaces.fb.GraphServiceEmitter","GraphServices"]',
            "client_trace_id": str(uuid.uuid4()),
        }
        resking = self.r.post(self.url, headers=self.head2, data=params)

    def additionsumbit(self):
        self.head2.update({"X-Fb-Friendly-Name": "FbBloksActionRootQuery-com.bloks.www.additional.profile.plus.creation.action.name.submit"})
        params = {
            "method": "post", "pretty": "false", "format": "json", "server_timestamps": "true",
            "locale": "id_ID", "purpose": "fetch",
            "fb_api_req_friendly_name": "FbBloksActionRootQuery-com.bloks.www.additional.profile.plus.creation.action.name.submit",
            "fb_api_caller_class": "graphservice", "client_doc_id": "119940804217734265480409226803",
            "fb_api_client_context": '{"is_background":false}',
            "variables": json.dumps({
                "params": {
                    "params": json.dumps({"params": json.dumps({
                        "client_input_params": {"profile_plus_id": "0", "name": self.name},
                        "server_params": {
                            "variant": 8, "referrer": "bookmark_create_action", "screen": "name",
                            "INTERNAL__latency_qpl_marker_id": 36707139,
                            "INTERNAL__latency_qpl_instance_id": 44928213200049, "creation_source": "android"
                        }
                    })}),
                    "bloks_versioning_id": "d1583f026cccd22345fea8de656bb1d8162dabcca3249d6a0610be47545ec31a",
                    "app_id": "com.bloks.www.additional.profile.plus.creation.action.name.submit"
                },
                "scale": "1.5", "use_native_entrypoint_for_stars_on_reels": True,
                "nt_context": {
                    "using_white_navbar": True, "styles_id": "6100e7e89411ccf67ace027cedecd84f",
                    "pixel_ratio": 1.5, "is_push_on": True, "debug_tooling_metadata_token": None,
                    "is_flipper_enabled": False,
                    "theme_params": [{"value": ["three_neutral_gray"], "design_system_name": "XMDS"}, {"value": [], "design_system_name": "FDS"}],
                    "bloks_version": "d1583f026cccd22345fea8de656bb1d8162dabcca3249d6a0610be47545ec31a"
                }
            }),
            "fb_api_analytics_tags": '["GraphServices"]',
            "client_trace_id": str(uuid.uuid4()),
        }
        resking = self.r.post(self.url, headers=self.head2, data=params)

    def finalcreate(self):
        self.head2.update({"X-Fb-Friendly-Name": "FbBloksActionRootQuery-com.bloks.www.additional.profile.plus.creation.action.category.submit"})
        params = {
            "method": "post", "pretty": "false", "format": "json", "server_timestamps": "true",
            "locale": "id_ID", "purpose": "fetch",
            "fb_api_req_friendly_name": "FbBloksActionRootQuery-com.bloks.www.additional.profile.plus.creation.action.category.submit",
            "fb_api_caller_class": "graphservice", "client_doc_id": "119940804217734265480409226803",
            "fb_api_client_context": '{"is_background":false}',
            "variables": json.dumps({
                "params": {
                    "params": json.dumps({"params": json.dumps({
                        "client_input_params": {
                            "entrypoint_logging_data": {"fb_profile_editing_session_entry_point": None, "field_edit_screen_entry_point": None},
                            "profile_plus_id": "0", "cp_upsell_declined": 0,
                            "off_platform_creator_reachout_id": "", "session_id": None,
                            "category_ids": ["2201", "180164648685982"],
                            "nav_chain": "com.bloks.www.additional.profile.plus.creation,com.bloks.www.additional.profile.plus.creation,,1778504139.506,144828353,,,,1778504139.506;com.bloks.www.additional.profile.plus.creation,com.bloks.www.additional.profile.plus.creation,,1778504112.481,56946930,,,,1778504112.481;com.bloks.www.unified.profile.creation,com.bloks.www.unified.profile.creation,sliding_panel_reset_on_app_background,1778504024.891,105632542,,,,1778504024.891"
                        },
                        "server_params": {
                            "referrer": "bookmark_create_action",
                            "INTERNAL__latency_qpl_marker_id": 36707139,
                            "creation_source": "android", "name": self.name, "variant": 8, "screen": "category",
                            "INTERNAL__latency_qpl_instance_id": 45025177700061
                        }
                    })}),
                    "bloks_versioning_id": "d1583f026cccd22345fea8de656bb1d8162dabcca3249d6a0610be47545ec31a",
                    "app_id": "com.bloks.www.additional.profile.plus.creation.action.category.submit"
                },
                "scale": "1.5", "use_native_entrypoint_for_stars_on_reels": True,
                "nt_context": {
                    "using_white_navbar": True, "styles_id": "6100e7e89411ccf67ace027cedecd84f",
                    "pixel_ratio": 1.5, "is_push_on": True, "debug_tooling_metadata_token": None,
                    "is_flipper_enabled": False,
                    "theme_params": [{"value": ["three_neutral_gray"], "design_system_name": "XMDS"}, {"value": [], "design_system_name": "FDS"}],
                    "bloks_version": "d1583f026cccd22345fea8de656bb1d8162dabcca3249d6a0610be47545ec31a"
                }
            }),
            "fb_api_analytics_tags": '["GraphServices"]',
            "client_trace_id": str(uuid.uuid4()),
        }
        resking = self.r.post(self.url, headers=self.head2, data=params)
        restext = resking.text
        if '"errors"' in restext and ('"code":1675030' in restext or 'field_exception' in restext):
            print(f"[✗] {self.uid} | Akun belum bisa buat profil baru (field_exception).")
            return False
        new_id = extract_new_profile_id(restext, self.uid)
        if new_id:
            print(f"[✓] Uid berhasil: {new_id}")
        else:
            print(f"[✓] {self.uid} | Profil baru berhasil dibuat: {self.name}")
        return True

    def _run_profile_cycle(self):
        self.name = random_name()
        print(f"\n[*] {self.uid} | Mulai buat profil: {self.name}")
        self.unifedprofile()
        self.additionalprofile()
        self.additionsumbit()
        return self.finalcreate()

    def run_loop(self):
        cycle = 1
        while True:
            print(f"\n[*] {self.uid} | Siklus ke-{cycle}")
            success = self._run_profile_cycle()
            if not success:
                print(f"[✗] {self.uid} | Akun gagal buat profil, thread dihentikan.")
                return
            print(f"[*] {self.uid} | Berhasil. Cooldown {COOLDOWN_SECONDS // 60} menit...")
            time.sleep(COOLDOWN_SECONDS)
            cycle += 1


if __name__ == "__main__":
    clear()
    filename = input("Masukkan nama file akun (contoh: akun.txt) : ").strip()
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
    except FileNotFoundError:
        print(f"[✗] File '{filename}' tidak ditemukan.")
        exit(1)

    print(f"[*] Total akun ditemukan: {len(lines)}\n")

    threads = []
    for i, line in enumerate(lines, 1):
        parts = line.split("|")
        if len(parts) < 3:
            print(f"[!] Baris {i} format salah (harus uid|password|email|totp), skip.")
            continue
        uid = parts[0].strip()
        pw = parts[1].strip()
        totp_seed = parts[3].split(">")[0].strip() if len(parts) >= 4 else ""

        print(f"{'='*60}")
        print(f"[{i}/{len(lines)}] Login akun: {uid}")
        print(f"{'='*60}")

        bot = CreatePage(uid, pw, totp_seed)
        if bot.login():
            print(f"[✓] {uid} | Login berhasil, memulai thread...")
            t = threading.Thread(target=bot.run_loop, name=f"Thread-{uid}", daemon=True)
            t.start()
            threads.append(t)
        else:
            print(f"[✗] {uid} | Login gagal, akun dilewati.")
        print()

    if not threads:
        print("[!] Tidak ada akun yang berhasil login.")
        exit(0)

    print(f"\n[*] {len(threads)} thread berjalan. Tekan Ctrl+C untuk berhenti.\n")
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\n[!] Dihentikan oleh pengguna.")
