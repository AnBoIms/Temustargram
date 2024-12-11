import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom"; // useNavigate 추가
import "./Main.css";
import MainNav from "./MainNav";
import Confetti from 'react-confetti';

import {Button} from '@nextui-org/react';
import confetti from 'canvas-confetti';

import tempImg from "../assets/temp2.jpg";
import kakao from "../assets/kakao.png";
import pangpang from "../assets/pang.png";
import downloadLogo from "../assets/downloadLogo.png";

// kakao 기능 동작을 위해 넣어준다.
// const { Kakao } = window;

const Output = () => {
    const imgRef = useRef(null);
    const navigate = useNavigate(); // navigate 훅 사용
    const location = useLocation();

    const [imageSrc, setImageSrc] = useState(null); // 이미지를 저장할 상태
    const [error, setError] = useState(null); // 에러 상태
    const confettiInstance = useRef(null); // Confetti 인스턴스

    const buttonRef = useRef(null); // 여기서 buttonRef를 정의합니다.

    // const realUrl = "http://localhost:3000" //나중에 배포시에 주소 바꾸기
    // // 로컬 주소 (localhost 3000 같은거)
    // const resultUrl = window.location.href;

    // useEffect(()=>{
    // 	// init 해주기 전에 clean up 을 해준다.
    //     Kakao.cleanup();
    //     // 자신의 js 키를 넣어준다.
    //     Kakao.init('c2cbb14eb64047ab9fe34925c8db79ad');
    //     // 잘 적용되면 true 를 뱉는다.
    //     console.log(Kakao.isInitialized());
    // },[]);

    

    useEffect(() => {
        if (location.state && location.state.result) {
            const base64Image = location.state.result;

            if (!base64Image.startsWith("data:image/")) {
                setImageSrc(`data:image/png;base64,${base64Image}`);
            } else {
                setImageSrc(base64Image);
            }
        } else {
            setError("이미지가 전달되지 않았습니다.");
        }
    }, [location.state]);

    const handleDownload = () => {
        if (imageSrc) {
            const link = document.createElement("a");
            link.href = imageSrc; // 이미지 소스 (Base64 or URL)
            link.download = "downloaded_image.jpg"; // 저장 파일명
            link.click();
        } else {
            console.error("Image source is not available for download.");
        }
    };

    // const handleGoToInsta = () => {
    //     navigate("/insta");
    // };

    const handleConfetti = () => {
        confetti({
            particleCount: 150, // 파티클 수
            spread: 70, // 퍼짐 범위
            origin: { x: 0.3, y: 0.5}, // 화면 중앙에서 효과 발생
        });
        confetti({
            particleCount: 150, // 파티클 수
            spread: 70, // 퍼짐 범위
            origin: { x: 0.7, y: 0.5}, // 화면 중앙에서 효과 발생
        });
    };

    // const shareKakao = () =>{

    //     Kakao.Share.sendDefault({
    //         objectType: 'feed',
    //         content: {
    //             title: '개인정보 안보임스',
    //             description: '개인정보 안보임스',
    //             imageUrl:
    //             'https://mud-kage.kakao.com/dn/NTmhS/btqfEUdFAUf/FjKzkZsnoeE4o19klTOVI1/openlink_640x640s.jpg',
    //             link: {
    //                 mobileWebUrl: realUrl,
    //             },
    //         },
    //         buttons: [
    //             {
    //                 title: '사진 가리러 가기',
    //                 link: {
    //                 mobileWebUrl: realUrl,
    //                 },
    //             },
    //             ],
    //         });
    // }

    return (
        <div>
            <MainNav />

            <div className="container" style={{ position: "relative" }}>
                {/* Confetti Canvas */}
                {/* <Confetti
                    refConfetti={(instance) => {
                        console.log("Confetti instance:", instance); // 디버깅 로그

                        confettiInstance.current = instance;
                        if (instance) console.log("Confetti instance set.");

                    }}
                    style={{
                        position: "absolute",
                        top: 0,
                        left: 0,
                        width: "100%",
                        height: "100%",
                        pointerEvents: "none",
                    }}
                /> */}

                <div className="text_output">
                    <h1>개인정보 안보임스!</h1>
                </div>
                <div className="result">
                    {imageSrc ? (
                        <div className="result_img">
                            <img src={imageSrc} ref={imgRef} alt="Result" />
                        </div>
                    ) : (
                        <div className="loader"></div>
                    )}
                </div>

                <div className="buttons">
                    <button className='share_button' onClick={() => {
                            shareKakao()
                        }}
                    >                     
                        <img className="share_icon" src={kakao} alt="Instagram" />
                    </button>
                    <Button
                        ref={buttonRef}
                        disableRipple
                        className="relative overflow-visible rounded-full hover:-translate-y-1 px-12 shadow-xl bg-background/30 after:content-[''] after:absolute after:rounded-full after:inset-0 after:bg-background/40 after:z-[-1] after:transition after:!duration-500 hover:after:scale-150 hover:after:opacity-0"
                        size="lg"
                        onPress={handleConfetti}
                        className = "share_button"
                    >
                        <img className="share_icon" src={pangpang} alt="pangpang" />
                    </Button>
                    <button className="share_button" onClick={handleDownload}>
                        <img
                            className="share_icon"
                            src={downloadLogo}
                            alt="Download"
                        />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Output;
